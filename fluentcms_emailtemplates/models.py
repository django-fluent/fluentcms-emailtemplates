from email.utils import formataddr
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models import PlaceholderField, ContentItemRelation, ContentItem
from fluentcms_emailtemplates.managers import EmailTemplateManager
from parler.models import TranslatableModel, TranslatedFields
from parler.utils.context import switch_language

__all__ = (
    'EmailContentItem',
    'EmailTemplate',
)


class EmailContentItem(ContentItem):
    """
    A tagging interface for all content items that are used in e-mails.
    """
    class Meta:
        abstract = True




@python_2_unicode_compatible
class EmailTemplate(TranslatableModel):
    """
    An e-mail template defined in the database.
    """
    name = models.CharField(_("Name"), max_length=200)
    slug = models.SlugField(_("Internal name"), help_text=_("This unique name can be used refer to this content in in code."))

    # The layout reffers to a template to use.
    layout = models.CharField(_("Layout"), max_length=100, default='default', choices=settings.FLUENTCMS_EMAILTEMPLATES_LAYOUTS)

    # Advanced settings to set a custom sender.
    sender_name = models.CharField(_("Sender name"), max_length=200, blank=True, null=True)
    sender_email = models.EmailField(_("Sender email"), blank=True, null=True)

    # Multisite support
    parent_site = models.ForeignKey(Site, editable=False, default=settings.SITE_ID)
    is_cross_site = models.BooleanField(_("Share between all sites"), blank=True, default=False,
        help_text=_("This allows contents to be shared between multiple sites in this project.<br>\n"
                    "Make sure that any URLs in the content work with all sites where the content is displayed."))

    # Allow subject to be different in other languages.
    # Also triggers multilingual support in the PlaceholderField() by default.
    translations = TranslatedFields(
        subject = models.CharField(_("Subject"), max_length=255, help_text=_("Placeholders such as <code>{first_name}</code> can be used here.")),
    )

    # The body contents is handled by the django-fluent-contents plugins.
    contents = PlaceholderField("email_templates", verbose_name=_("Contents"), plugins=settings.FLUENTCMS_EMAILTEMPLATES_PLUGINS)

    # Adding the reverse relation for ContentItem objects
    # causes the admin to list the related objects when deleting this model.
    contentitem_set = ContentItemRelation()

    objects = EmailTemplateManager()

    class Meta:
        verbose_name = _("Email template")
        verbose_name_plural = _("Email templates")
        ordering = ('name',)
        unique_together = (
            ('parent_site', 'slug'),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        with switch_language(self):
            return reverse('admin:fluentcms_emailtemplates_emailtemplate.preview', args=(self.pk,))

    def get_from_email(self):
        """
        Format the sender name for the "From" field.

        :param user: Optional user that is sending the e-mail message.
        :type user: django.contrib.auth.models.User
        :return: A "Name <email>" formatted string.
        :rtype: str
        """
        if self.sender_email is not None:
            return formataddr((self.sender_email, self.sender_name or self.sender_email))
        else:
            return settings.DEFAULT_FROM_EMAIL

    def get_html_templates(self):
        """
        The HTML e-mail templates to use.
        """
        return [
            'fluentcms_emailtemplates/emails/{slug}/{layout}.html'.format(slug=self.slug, layout=self.layout),
            'fluentcms_emailtemplates/emails/{layout}.html'.format(layout=self.layout),
        ]

    def get_text_templates(self):
        """
        The plain-text e-mail templates to use.
        """
        return [
            'fluentcms_emailtemplates/emails/{slug}/{layout}.txt'.format(slug=self.slug, layout=self.layout),
            'fluentcms_emailtemplates/emails/{layout}.txt'.format(layout=self.layout),
        ]

    def get_content(self, base_url, context=None, user=None):
        """
        Return the content for an email message, rendered with this template.

        :type base_url: str
        :type context: dict | None
        :type user: django.contrib.auth.models.User
        :rtype: fluentcms_emailtemplates.rendering.EmailContent
        """
        # Don't really like the idea of adding rendering functions to the model,
        # but having this shortcut is convenient. You can always construct your own
        # EmailMessage
        from .rendering import render_email_template
        return render_email_template(self, base_url, extra_context=context, user=user)

    def get_email_message(self, base_url=None, context=None, user=None, from_email=None,
                          to=None, cc=None, bcc=None, headers=None, attachments=None, connection=None):
        """
        Get an e-mail message for a given EmailTemplate.

        This is a convenience function that uses :func:`get_content`
        to build an :class:`~django.core.mail.EmailMultiAlternatives` object.

        :rtype: EmailMultiAlternatives
        """
        # This is purposefully split from send_email_template(),
        # so things like admin previews can be implemented too.
        content = self.get_content(base_url, context=context, user=user)
        return EmailMultiAlternatives(
            subject=content.subject,
            body=content.text,
            from_email=from_email or self.get_from_email(),
            to=to,
            bcc=bcc,
            # This is the default argument ordering,
            # placed in different order in this function.
            connection=connection,
            attachments=attachments,
            headers=headers,
            alternatives=[(content.html, "text/html; charset=utf-8")],
            cc=cc
        )
