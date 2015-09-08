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

    fieldsets = (
        (None, {
            'fields': ('html',),
        }),
        (_("Other versions"), {
            'fields': ('text',),
            'classes': ('collapse',),
        }),
    )

    def render_html(self, request, instance, context):
        # Included in a DIV, so the next item will be displayed below.
        return mark_safe(replace_fields(instance.html, context))

    def render_text(self, request, instance, context):
        if instance.text:
            # When a custom text is provided, use that.
            return replace_fields(instance.text, context)
        else:
            # Otherwise, let the default implementation do it's work.
            # It will base the text version off the HTML code.
            return super(EmailTextPlugin, self).render_text(request, instance, context)
