from django.core.exceptions import ImproperlyConfigured
from fluentcms_emailtemplates.extensions import EmailContentPlugin
from fluent_contents.extensions import plugin_pool
from .models import OrderSummaryEmailItem

try:
    from django.apps import apps  # Django 1.7+
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model


@plugin_pool.register
class OrderSummaryEmailPlugin(EmailContentPlugin):
    """
    Plugin for rendering TEXT content in email templates.
    """
    model = OrderSummaryEmailItem
    render_html_template = 'fluentcms_emailtemplates/plugins/oscar_email/order_summary.html'
    render_text_template = 'fluentcms_emailtemplates/plugins/oscar_email/order_summary.txt'

    def get_context(self, request, instance, **kwargs):
        context = super(EmailContentPlugin, self).get_context(request, instance, **kwargs)
        if 'order' in context:
            context['order_number'] = context['order'].number  # for consistency
            context['order_currency'] = context['order'].currency
        else:
            # Go for preview mode options
            context['order_currency'] = 'USD'

            if 'order_number' in context:
                Order = get_model('order', "Order")
                number = context['order_number']
                try:
                    order = Order.objects.get(number=number)
                except Order.DoesNotExist:
                    raise ImproperlyConfigured("Invalid order_number in context: {0}".format(number))
                context['order'] = order
                context['order_currency'] = order.currency

        return context
