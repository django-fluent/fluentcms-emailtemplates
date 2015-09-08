from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import PluginHtmlField
from fluentcms_emailtemplates.models import EmailContentItem


@python_2_unicode_compatible
class EmailTextItem(EmailContentItem):
    """
    ContentItem for e-mail texts.
    """
    html = PluginHtmlField(_('Text'), help_text=_("Placeholders such as <code>{first_name}</code>, <code>{last_name}</code> and <code>{full_name}</code> can be used here."))
    text = models.TextField(_("Plain text version"), blank=True, null=True, help_text=_("If left empty, the HTML contents will be used to generate a plain-text version."))

    class Meta:
        verbose_name = _("E-mail text")
        verbose_name_plural = _("E-mail text")

    def __str__(self):
        return Truncator(self.text or strip_tags(self.html)).words(20)
