from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Container, Department, Organisation, Parcel, Rule


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    filter_horizontal = ("users",)


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    list_display = ("id", "shipping_date", "organisation")


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "organisation")
    search_fields = ("name", "organisation__name")
    list_filter = ("organisation",)
    ordering = ("name",)


class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        "recipient_name",
        "street",
        "house_number",
        "postal_code",
        "city",
        "weight",
        "value",
        "container",
        "organisation_name",
    )
    search_fields = ("recipient_name", "postal_code", "city")
    list_filter = ("city", "container__organisation")
    ordering = ("recipient_name",)


admin.site.register(Parcel, ParcelAdmin)
