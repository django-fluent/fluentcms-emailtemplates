from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import six
from django.utils.decorators import method_decorator
from django.views.generic.detail import BaseDetailView
from fluentcms_emailtemplates.models import EmailTemplate
from fluentcms_emailtemplates.rendering import render_email_template
from parler.views import LanguageChoiceMixin
from .conf import settings


class StaffMemberRequiredMixin(object):
    """
    Require staff member, but redirect to admin login.
    """
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffMemberRequiredMixin, self).dispatch(request, *args, **kwargs)


class EmailPreviewView(StaffMemberRequiredMixin, LanguageChoiceMixin, BaseDetailView):
    """
    Preview for an e-mail template
    """
    model = EmailTemplate
    template_name = 'admin/fluentcms_emailtemplates/preview.html'

    def get_context_data(self, **kwargs):
        context = super(EmailPreviewView, self).get_context_data(**kwargs)
        email = render_email_template(self.object,
            base_url=self.request.build_absolute_uri('/'),
            extra_context=settings.FLUENTCMS_EMAILTEMPLATES_PREVIEW_CONTEXT,
            user=self.request.user,
        )
        context['email'] = email
        return context

    def render_to_response(self, context, **response_kwargs):
        # Allow fetching a raw HTML or text version.
        # Will render in the template otherwise.
        format = self.request.GET.get('format') or 'html'

        email = context['email']
        if format in ('text', 'txt'):
            return HttpResponse(six.text_type(email.text), content_type='text/plain; charset=utf8')
        else:
            return HttpResponse(six.text_type(email.html), content_type='text/html; charset=utf8')
