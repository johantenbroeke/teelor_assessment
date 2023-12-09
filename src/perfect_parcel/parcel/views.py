import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic.list import ListView

from .models import Parcel
from .services import ContainerXMLParser

logger = logging.getLogger(__name__)


class ToggleParcelProcessedView(LoginRequiredMixin, View):
    """Toggle the processed status of a parcel"""

    def post(self, request, *args, **kwargs):
        parcel_id = self.kwargs.get("pk")
        parcel = Parcel.objects.get(id=parcel_id)
        parcel.processed = not parcel.processed
        parcel.save()
        return HttpResponseRedirect(reverse("organisation_parcels"))


class UserOrganisationParcelListView(LoginRequiredMixin, ListView):
    """List all parcels for the user's organisation"""

    model = Parcel
    template_name = "user_organisation_parcels.html"  # Path to your template
    context_object_name = "parcels"

    def get_queryset(self):
        user_organisations = self.request.user.organisations.all()
        return Parcel.objects.filter(container__organisation__in=user_organisations)


@method_decorator(require_http_methods(["GET", "POST"]), name="dispatch")
class UploadXMLView(View):
    """Upload container XML file"""

    template_name = "upload.html"

    def post(self, request, *args, **kwargs):
        organisation = request.user.organisations.first()
        if not organisation:
            return HttpResponse("No organisation associated with this user.")

        try:
            ContainerXMLParser(request.FILES["file"], organisation).parse()
        except Exception as e:
            logger.exception(e)
            return HttpResponse("Error processing XML file", status=400)

        return HttpResponseRedirect(reverse("organisation_parcels"))

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class UserLoginView(LoginView):
    """Login view for non admin users"""

    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("organisation_parcels")
