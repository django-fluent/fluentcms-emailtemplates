from appconf import AppConf
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'settings',
    'EmailTemplatesConf',
)

class EmailTemplatesConf(AppConf):
    """
    All configuration settings, which are loaded into django.conf.settings
    """
    # Possible template layouts
    LAYOUTS = (
        ('default', _("Default")),
    )

    # Possible plugins to use
    # Defaults to FLUENT_CONTENTS_PLACEHOLDER_CONFIG['emailtemplates_html']
    PLUGINS = None

    # Enable multisite support by default
    FILTER_SITE_ID = True

    # Optionally allow developers to share email templates between all sites in a multisite setup.
    ENABLE_CROSS_SITE = False

    # Add extras context data for an e-mail preview.
    PREVIEW_CONTEXT = {}

    class Meta:
        prefix = 'FLUENTCMS_EMAILTEMPLATES'
