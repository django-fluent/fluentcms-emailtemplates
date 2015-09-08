from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from fluentcms_emailtemplates.models import EmailContentItem


@python_2_unicode_compatible
class OrderSummaryEmailItem(EmailContentItem):
    """
    Content of the order.
    """
    class Meta:
        verbose_name = _("Oscar order summary")
        verbose_name_plural = _("Oscar order summaries")

    def __str__(self):
        return _("Order summary")
