import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class Organisation(models.Model):
    """This defines an organisation owning containers and departments. Users can be associated with an organisation"""

    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="organisations")

    def __str__(self):
        return self.name


class Department(models.Model):
    """This defines a department that can be allocated to a parcel."""

    slug = models.SlugField(
        primary_key=True, max_length=25, default="default", null=False, editable=True
    )
    name = models.CharField(max_length=255)
    organisation = models.ForeignKey(
        Organisation, related_name="departments", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Container(models.Model):
    """This defines a container that contains parcels."""

    id = models.CharField(primary_key=True, max_length=255, editable=False)
    shipping_date = models.DateTimeField()
    organisation = models.ForeignKey(
        Organisation, related_name="containers", on_delete=models.CASCADE
    )


class Parcel(models.Model):
    """This defines a parcel that is contained in a container."""

    container = models.ForeignKey(
        Container, related_name="parcels", on_delete=models.CASCADE
    )
    recipient_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    processed = models.BooleanField(default=False)

    def organisation_name(self):
        return self.container.organisation.name

    def allocated_departments(self):
        """returns the departments that have been allocated to this parcel."""
        selected_departments = []
        departments = self.container.organisation.departments.all()
        rule = self.container.organisation.rules.first()
        if not rule:
            return []
        try:
            rule.execute(self, departments, selected_departments)
        except NameError as e:
            logger.exception("Illegal python code in rule: %s", e)
            return []
        return selected_departments


class Rule(models.Model):
    """
    This defines a rule for a specific organisation. The rule is written in Python and can only access the following variables:
    - parcel: the parcel for which the rule is executed
    - departments: a queryset of all departments of the organisation
    - selected_departments: a list of departments that have been selected by the rule

    Example:

    if self.value > 1000:
        selected_departments.append(departments.filter(slug='insurance').first())
    if self.weight <= 1:
        selected_departments.append(departments.filter(slug='mail').first())
    elif self.weight <= 10:
        selected_departments.append(departments.filter(slug='regular').first())
    else:
        selected_departments.append(departments.filter(slug='heavy').first())
    """

    organisation = models.ForeignKey(
        Organisation, related_name="rules", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    python_code = models.TextField()

    def execute(self, parcel, departments, selected_departments):
        """Restrict the execution of the python code to the given variables."""
        restricted_globals = {"__builtins__": {}}
        local_variables = {
            "parcel": parcel,
            "departments": departments,
            "selected_departments": selected_departments,
        }
        exec(str(self.python_code), restricted_globals, local_variables)

    def __str__(self):
        return self.name
