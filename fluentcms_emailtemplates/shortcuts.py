"""
Short functions to send an email.
"""
from fluentcms_emailtemplates.models import EmailTemplate


def send_email_template(slug, base_url=None, context=None, user=None,
                       to=None, cc=None, bcc=None, attachments=None, headers=None, connection=None, fail_silently=False):
    """
    Shortcut to send an email template.
    """
    email_template = EmailTemplate.objects.get_for_slug(slug)

    email = email_template.get_email_message(
        base_url, context, user,
        to=to, cc=cc, bcc=bcc,
        attachments=attachments, headers=headers, connection=connection
    )

    return email.send(fail_silently=fail_silently)
