# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views import generic as generic_views

from .forms import JobOfferForm
from .models import Sponsor
from .tasks import send_job_offer


class JobOffer(generic_views.FormView):
    template_name = 'sponsorship/send_job_offer.html'
    form_class = JobOfferForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('sponsorship.add_joboffer'):
            messages.error(request, _('You do not have permission to send job offers.'))
            return HttpResponseRedirect('/')
        return super(JobOffer, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        send_job_offer.delay(form.cleaned_data)
        messages.success(self.request, _('Job offer sent'))
        return HttpResponseRedirect(self.request.path)

job_offer = JobOffer.as_view()


def list_sponsors(request):
    """
    This view lists all sponsors ordered by their level and name.
    """
    sponsors = Sponsor.objects.filter(active=True) \
                              .select_related('level') \
                              .order_by('level__order', 'name') \
                              .all()
    return TemplateResponse(
        request=request,
        context={
            'sponsors': sponsors,
        },
        template='sponsorship/sponsor_list.html'
    )
