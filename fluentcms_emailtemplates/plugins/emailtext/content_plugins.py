from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from fluentcms_emailtemplates.extensions import EmailContentPlugin
from fluent_contents.extensions import plugin_pool
from fluentcms_emailtemplates.rendering import replace_fields
from .models import EmailTextItem


@plugin_pool.register
class EmailTextPlugin(EmailContentPlugin):
    """
    Plugin for rendering TEXT content in email templates.
    """
    model = EmailTextItem
    admin_init_template = "admin/fluentcms_emailtemplates/plugins/emailtext/admin_init.html"  # TODO: remove the need for this.
    render_replace_context_fields = True

    fieldsets = (
        (None, {
            'fields': ('html', 'text'),
        }),
    )

    def render_html(self, request, instance, context):
        # Included in a DIV, so the next item will be displayed below it.
        html = mark_safe(u"<div>{0}</div>".format(instance.html))
        html = replace_fields(html, context)  # Do manually because render_html() was overwritten
        return html

    def render_text(self, request, instance, context):
        if instance.text:
            # When a custom text is provided, use that.
            text = instance.text
            text = replace_fields(text, context, autoescape=False)
            return text
        else:
            # Otherwise, let the default implementation do it's work.
            # It will base the text version off the HTML code.
            return super(EmailTextPlugin, self).render_text(request, instance, context)
