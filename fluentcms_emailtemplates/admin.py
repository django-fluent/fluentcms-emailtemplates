from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from fluentcms_emailtemplates.views import EmailPreviewView
from parler.admin import TranslatableAdmin
from fluent_contents.admin import PlaceholderFieldAdmin
from fluent_utils.dry.admin import MultiSiteAdminMixin
from .models import EmailTemplate
from .conf import settings
from parler.utils import get_language_title


class EmailTemplateAdmin(MultiSiteAdminMixin, TranslatableAdmin, PlaceholderFieldAdmin):
    """
    Admin screen for the shared content, displayed in the global Django admin.
    """
    filter_site = settings.FLUENTCMS_EMAILTEMPLATES_FILTER_SITE_ID
    preview_template = "admin/fluentcms_emailtemplates/preview.html"
    list_display = ('name', 'slug')
    ordering = ('slug',)

    def get_prepopulated_fields(self, request, obj=None):
        # Needed instead of prepopulated_fields=.. for django-parler
        return {
            'slug': ('name',)
        }

    # Using declared_fieldsets for Django 1.4, otherwise fieldsets= would work too.
    declared_fieldsets = (
        (None, {
            'fields': ('name', 'layout',),
        }),
        (_("Email content"), {
            'fields': ('subject', 'contents'),
        }),
        (_("Delivery settings"), {
            'fields': ('sender_name', 'sender_email'),
        }),
        (_("Advanced settings"), {
            'fields': ('slug',),
            'classes': ('collapse',),
        }),
    )

    if settings.FLUENTCMS_EMAILTEMPLATES_ENABLE_CROSS_SITE:
        declared_fieldsets[2][1]['fields'] += ('is_cross_site',)

    def get_urls(self):
        base_urls = super(EmailTemplateAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            url(r'^(.+)/preview/$', self.admin_site.admin_view(self.preview_view), name='%s_%s_preview' % info),
            url(r'^(?P<pk>.+)/preview/frame/$', self.admin_site.admin_view(EmailPreviewView.as_view()), name='%s_%s_preview_frame' % info),
        ] + base_urls

    def preview_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        email_format = request.GET.get('format', None) or 'html'
        TITLES = {
            'html': _("Preview HTML: {subject}"),
            'text': _("Preview plain text: {subject}"),
        }
        TITLES['txt'] = TITLES['text']
        if email_format not in TITLES:
            email_format = 'html'

        context = {
            'title': TITLES[email_format].format(subject=obj.subject),
            'app_label': obj._meta.app_label,
            'opts': obj._meta,
            'media': self.media,
            'object': obj,
            'email_format': email_format
        }

        # Add django-parler language tabs (copied from TranslatableAdmin.render_change_form())
        lang_code = self.get_form_language(request, obj)
        lang = get_language_title(lang_code)

        available_languages = self.get_available_languages(obj)
        language_tabs = self.get_language_tabs(request, obj, available_languages)
        context['language_tabs'] = language_tabs
        if language_tabs:
            context['title'] = '%s (%s)' % (context['title'], lang)

        return TemplateResponse(request, self.preview_template, context)


admin.site.register(EmailTemplate, EmailTemplateAdmin)
