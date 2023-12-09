"""
URL configuration for perfect_parcel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from parcel import views

urlpatterns = [
    path("", views.UserLoginView.as_view(), name="login"),
    path("admin/", admin.site.urls),
    path("upload_xml/", views.UploadXMLView.as_view(), name="upload_xml"),
    path(
        "parcels/",
        views.UserOrganisationParcelListView.as_view(),
        name="organisation_parcels",
    ),
    path(
        "parcel/<int:pk>/toggle-processed/",
        views.ToggleParcelProcessedView.as_view(),
        name="toggle_processed",
    ),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
