from __future__ import unicode_literals
import cgi
import logging
import re
from bs4 import BeautifulSoup
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeData
from django.contrib.auth.models import AnonymousUser
from django.template import RequestContext
from django.template.loader import render_to_string
from django.test import RequestFactory
from urlparse import urlsplit, urljoin
from html2text import HTML2Text
from html2text import config
from fluent_contents import appsettings as fc_appsettings
from parler.utils.context import switch_language

SCALAR_TYPES = six.integer_types + six.string_types + (float,)
OBJECT_TYPES = (object,)
CONFIG_DEFAULT = object()

# Parse str.format() syntax.
# Does not support dict[item] but this is not expected to be needed.
# https://docs.python.org/2/library/string.html#formatstrings
RE_FORMAT = re.compile(
    '\{(?P<var>[a-zA-Z0-9_]+)'       # a simple python var name
    '(\.(?P<attr>[a-zA-Z0-9_]+))?'   # dot + attribute
    '(?P<format>:[^}]+)?\}'          # str.format() can use any char as fill
)

logger = logging.getLogger(__name__)


def html_to_text(html, base_url='', bodywidth=CONFIG_DEFAULT):
    """
    Convert a HTML mesasge to plain text.
    """
    def _patched_handle_charref(c):
        self = h
        charref = self.charref(c)
        if self.code or self.pre:
            charref = cgi.escape(charref)
        self.o(charref, 1)

    def _patched_handle_entityref(c):
        self = h
        entityref = self.entityref(c)
        if self.code or self.pre:  # this expression was inversed.
            entityref = cgi.escape(entityref)
        self.o(entityref, 1)

    h = HTML2Text(baseurl=base_url, bodywidth=config.BODY_WIDTH if bodywidth is CONFIG_DEFAULT else bodywidth)
    h.handle_entityref = _patched_handle_entityref
    h.handle_charref = _patched_handle_charref
    return h.handle(html).rstrip()



def replace_fields(text, context, autoescape=None, errors='inline'):
    """
    Allow simple field replacements, using the python str.format() syntax.

    When a string is passed that is tagged with :func:`~django.utils.safestring.mark_safe`,
    the context variables will be escaped before replacement.

    This function is used instead of lazily using Django templates,
    which can also the {% load %} stuff and {% include %} things.
    """
    raise_errors = errors == 'raise'
    ignore_errors = errors == 'ignore'
    inline_errors = errors == 'inline'

    if autoescape is None:
        # When passing a real template context, use it's autoescape setting.
        # Otherwise, default to true.
        autoescape = getattr(context, 'autoescape', True)

    is_safe_string = isinstance(text, SafeData)
    if is_safe_string and autoescape:
        escape_function = conditional_escape
        escape_error = lambda x: u"<span style='color:red;'>{0}</span>".format(x)
    else:
        escape_function = force_text
        escape_error = six.text_type

    # Using str.format() may raise a KeyError when some fields are not provided.
    # Instead, simulate its' behavior to make sure all items that were found will be replaced.
    start = 0
    new_text = []
    for match in RE_FORMAT.finditer(text):
        new_text.append(text[start:match.start()])
        start = match.end()

        # See if the element was found
        key = match.group('var')
        try:
            value = context[key]
        except KeyError:
            logger.debug("Missing key %s in email template %s!", key, match.group(0))
            if raise_errors:
                raise
            elif ignore_errors:
                new_text.append(match.group(0))
            elif inline_errors:
                new_text.append(escape_error("!!missing {0}!!".format(key)))
            continue

        # See if further processing is needed.
        attr = match.group('attr')
        if attr:
            try:
                value = getattr(value, attr)
            except AttributeError:
                logger.debug("Missing attribute %s in email template %s!", attr, match.group(0))
                if raise_errors:
                    raise
                elif ignore_errors:
                    new_text.append(match.group(0))
                elif inline_errors:
                    new_text.append(escape_error("!!invalid attribute {0}.{1}!!".format(key, attr)))
                continue

        format = match.group('format')
        if format:
            try:
                template = u"{0" + format + "}"
                value = template.format(value)
            except ValueError:
                logger.debug("Invalid format %s in email template %s!", format, match.group(0))
                if raise_errors:
                    raise
                elif ignore_errors:
                    new_text.append(match.group(0))
                elif inline_errors:
                    new_text.append(escape_error("!!invalid format {0}!!".format(format)))
                continue
        else:
            value = escape_function(value)

        # Add the value
        new_text.append(value)

    # Add remainder, and join
    new_text.append(text[start:])
    new_text = u"".join(new_text)

    # Convert back to safestring if it was passed that way
    if is_safe_string:
        return mark_safe(new_text)
    else:
        return new_text


def render_email_template(email_template, base_url, extra_context=None, user=None):
    """
    Render the email template.

    :type email_template: fluentcms_emailtemplates.models.EmailTemplate
    :type base_url: str
    :type extra_context: dict | None
    :type user: django.contrib.auth.models.User
    :return: The subject, html and text content
    :rtype: fluentcms_emailtemplates.rendering.EmailContent
    """
    dummy_request = _get_dummy_request(base_url, user)
    context_user = user or extra_context.get('user', None)

    context_data = {
        'request': dummy_request,
        'email_template': email_template,
        'email_format': 'html',
        'user': user,
        # Common replacements
        'first_name': context_user.first_name if context_user else '',
        'last_name': context_user.last_name if context_user else '',
        'full_name': context_user.get_full_name() if context_user else '',
        'email': context_user.email if context_user else '',
        'site': extra_context.get('site', None) or {
            'domain': dummy_request.get_host(),
            'name': dummy_request.get_host(),
        }
    }
    if extra_context:
        context_data.update(extra_context)

    # Make sure the templates and i18n are identical to the emailtemplate language.
    # This is the same as the current Django language, unless the object was explicitly fetched in a different language.
    with switch_language(email_template):
        # Get the body content
        context_data['body'] = _render_email_placeholder(dummy_request, email_template, base_url, context_data)
        context_data['subject'] = subject = replace_fields(email_template.subject, context_data, autoescape=False)

        # Merge that with the HTML templates.
        context_instance = RequestContext(dummy_request)
        context_instance.update(context_data)
        html = render_to_string(email_template.get_html_templates(), context_instance=context_instance)
        html, url_changes = _make_links_absolute(html, base_url)

        # Render the Text template.
        # Disable auto escaping
        context_instance['email_format'] = 'text'
        context_instance.autoescape = False
        text = render_to_string(email_template.get_text_templates(), context_instance=context_instance)
        text = _make_text_links_absolute(text, url_changes)

        return EmailContent(subject, text, html)


def _get_dummy_request(base_url, user):
    """
    Create a dummy request.
    Use the ``base_url``, so code can use ``request.build_absolute_uri()`` to create absolute URLs.
    """
    split_url = urlsplit(base_url)
    is_secure = split_url[0] == 'https'
    dummy_request = RequestFactory(HTTP_HOST=split_url[1]).get('/', secure=is_secure)
    dummy_request.is_secure = lambda: is_secure
    dummy_request.user = user or AnonymousUser()
    return dummy_request



def _render_email_placeholder(request, email_template, base_url, context):
    """
    Internal rendering of the placeholder/contentitems.

    This a simple variation of render_placeholder(),
    making is possible to render both a HTML and text item in a single call.
    Caching is currently not implemented.

    :rtype: fluentcms_emailtemplates.rendering.EmailBodyContent
    """
    placeholder = email_template.contents
    items = placeholder.get_content_items(email_template)

    if not items:  # NOTES: performs query
        # There are no items, fetch the fallback language.
        language_code = fc_appsettings.FLUENT_CONTENTS_DEFAULT_LANGUAGE_CODE
        items = placeholder.get_content_items(email_template, limit_parent_language=False).translated(language_code)

    html_fragments = []
    text_fragments = []

    for instance in items:
        plugin = instance.plugin
        html_part = _render_html(plugin, request, instance, context)
        text_part = _render_text(plugin, request, instance, context, base_url)
        html_fragments.append(html_part)
        text_fragments.append(text_part)

    html_body = u"".join(html_fragments)
    text_body = u"".join(text_fragments)

    return EmailBodyContent(text_body, html_body)


def _render_html(plugin, request, instance, context):
    if hasattr(plugin, 'render_html'):
        # Our custom EmailContentPlugin
        return plugin.render_html(request, instance, context)
    else:
        # Regular django-fluent-contents plugin
        return plugin.render(request, instance)


def _render_text(plugin, request, instance, context, base_url):
    if hasattr(plugin, 'render_text'):
        # Our custom EmailContentPlugin
        return plugin.render_text(request, instance, context)
    else:
        # Regular django-fluent-contents plugin
        return html_to_text(plugin.render(request, instance), base_url)


def _make_links_absolute(html, base_url):
    """
    Make all links absolute.
    """
    url_changes = []

    soup = BeautifulSoup(html)
    for tag in soup.find_all('a', href=True):
        old = tag['href']
        fixed = urljoin(base_url, old)
        if old != fixed:
            url_changes.append((old, fixed))
            tag['href'] = fixed

    for tag in soup.find_all('img', src=True):
        old = tag['src']
        fixed = urljoin(base_url, old)
        if old != fixed:
            url_changes.append((old, fixed))
            tag['src'] = fixed

    return mark_safe(six.text_type(soup)), url_changes


def _make_text_links_absolute(text, url_changes):
    # Order by length to avoid accidental text replacements
    url_changes = sorted(url_changes, key=lambda item: (-len(item[0]), item[0]))
    for old, fixed in url_changes:
        # Don't replace this kind of URL:
        if old == '/':
            continue

        # Avoid accidental replacements. Be strict in what kind of tokens should be around it.
        text = re.sub(u'(^|[:.\s<\r\n])%s($|[>\s\r\n])' % old, r"\1%s\2" % fixed, text)

    # TODO: make sure the are no accidental replacements.
    return text


class EmailContent(object):
    def __init__(self, subject, text, html):
        self.subject = subject
        self.text = text
        self.html = html


class EmailBodyContent(object):
    def __init__(self, text, html):
        self.text = text
        self.html = html
