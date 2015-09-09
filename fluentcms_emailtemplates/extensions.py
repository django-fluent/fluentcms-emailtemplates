from fluent_contents.extensions import ContentPlugin, PluginContext
from fluentcms_emailtemplates.rendering import html_to_text, replace_fields


class EmailContentPlugin(ContentPlugin):
    """
    A plugin for e-mail templates, that can render both text and HTML.

    The custom rendering functions are ``render_html`` and ``render_text``.
    In case the regular functions are used (e.g. ``{% render_placeholder %}`` or ``fluent_contents.rendering``),
    the HTML version of the plugin is rendered.

    The regular rendering is provided as fallback,
    please use the :func:`render_html` and :func:`render_text` instead.
    """

    #: The template to use for HTML rendering
    render_html_template = None

    #: The template to use for plain text rendering.
    #: When no template is given, the HTML output is used to generate the plain text version.
    render_text_template = None

    #: Whether the parent context should be exposed to the plugin templates, and replace variables
    merge_parent_context = True

    #: Whether the default :meth:`render_html` and :meth:`render_text` should call
    #: the :func:`~fluentcms_emailtemplates.rendering.replace_fields` on the output.
    render_replace_context_fields = False


    # -- Fallback logic

    def render(self, request, instance, **kwargs):
        # If you'd ever use {% render_placeholder %} on this,
        # the HTML template will be rendered
        return self.render_html(request, instance, context={})

    def get_global_context(self, request, instance):
        """
        Provide global context data.
        """
        return {}

    def get_context(self, request, instance, **kwargs):
        # Pass email_format to the templates
        context = super(EmailContentPlugin, self).get_context(request, instance, **kwargs)

        parent_context = kwargs.get('parent_context', {})
        email_context = {
            'email_format': kwargs.get('email_format', None),
            'parent_context': parent_context,
        }
        if self.merge_parent_context:
            email_context.update(**parent_context)
        email_context.update(**context)
        return email_context

    def get_render_template(self, request, instance, email_format=None, **kwargs):
        if email_format == 'text':
            return self.render_text_template or self.render_template
        elif email_format == 'html':
            return self.render_html_template or self.render_template
        else:
            # Take the HTML template in case the regular render() is used.
            return super(EmailContentPlugin, self).get_render_template(request, instance, **kwargs)


    # -- Split rendering modes

    def render_html(self, request, instance, context):
        """
        Custom rendering function for HTML output
        """
        render_template = self.get_render_template(request, instance, email_format='html')
        if not render_template:
            return str(u"{No HTML rendering defined for class '%s'}" % self.__class__.__name__)

        instance_context = self.get_context(request, instance, email_format='html', parent_context=context)
        instance_context['email_format'] = 'html'

        html = self.render_to_string(request, render_template, instance_context)
        if self.render_replace_context_fields:
            html = replace_fields(html, instance_context)  # pass safe-string
        return html

    def render_text(self, request, instance, context):
        """
        Custom rendering function for HTML output
        """
        render_template = self.get_render_template(request, instance, email_format='text')
        if not render_template:
            # If there is no TEXT variation, create it by removing the HTML tags.
            base_url = request.build_absolute_uri('/')
            html = self.render_html(request, instance, context)
            return html_to_text(html, base_url)

        instance_context = self.get_context(request, instance, email_format='text', parent_context=context)
        instance_context['email_format'] = 'text'

        text = self.render_to_string(request, render_template, instance_context)
        text = text + ""  # Avoid being a safestring
        if self.render_replace_context_fields:
            text = replace_fields(text, instance_context, autoescape=False)
        return text

    def render_to_string(self, request, template, context, content_instance=None):
        if content_instance is None:
            # Disable HTML escaping for plain text email.
            content_instance = PluginContext(request)
            if context['email_format'] == 'text':
                content_instance.autoescape = False
        return super(EmailContentPlugin, self).render_to_string(request, template, context, content_instance=content_instance)
