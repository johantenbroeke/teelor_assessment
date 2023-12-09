import pytest

from parcel.models import Container, Department, Organisation, Parcel, Rule


@pytest.fixture(
    name="rule",
    params=[
        (
            "Rule 1",
            "if parcel.weight < 100: selected_departments.append(departments.filter(slug='department-1').first())",
        ),
        (
            "Rule 2",
            "if parcel.value > 2000: selected_departments.append(departments.filter(slug='department-2').first())",
        ),
        (
            "Rule 3",
            "if parcel.city == 'Oldenzaal': selected_departments.extend([departments.filter(slug='department-1').first(), departments.filter(slug='department-2').first()])",
        ),
        ("Rule 4", "print('Hello World')"),
    ],
)
def rule_fixture(request):
    return request.param


@pytest.fixture(name="parcel")
def parcel_fixture(rule):
    rule_name, rule_code = rule
    organisation = Organisation.objects.create(name="Test Organisation")
    Rule.objects.create(
        organisation=organisation, python_code=rule_code, name=rule_name
    )
    Department.objects.create(
        name="Department 1", organisation=organisation, slug="department-1"
    )
    Department.objects.create(
        name="Department 2", organisation=organisation, slug="department-2"
    )
    container = Container.objects.create(
        id=8520442,
        shipping_date="2023-12-08T11:25:22.795540",
        organisation=organisation,
    )
    parcel = Parcel.objects.create(
        container=container,
        recipient_name="Recipient 1",
        street="Street 1",
        house_number="88",
        postal_code="79906",
        city="Oldenzaal",
        weight=99,
        value=3000,
        processed=False,
    )
    return parcel


@pytest.mark.django_db
class TestAllocationRules:
    def test_allocation_of_parcel(self, parcel, rule, caplog):
        result = parcel.allocated_departments()
        if rule[0] == "Rule 1":
            assert len(result) == 1
            assert result[0].name == "Department 1"
        elif rule[0] == "Rule 2":
            assert len(result) == 1
            assert result[0].name == "Department 2"
        elif rule[0] == "Rule 3":
            assert len(result) == 2
            assert result[0].name == "Department 1"
            assert result[1].name == "Department 2"
        elif rule[0] == "Rule 4":  # globals should be empty
            assert (
                "Illegal python code in rule: name 'print' is not defined"
                in caplog.text
            )
            assert len(result) == 0

    def test_allocation_of_parcel_with_no_rule(self, parcel):
        parcel.container.organisation.rules.all().delete()
        result = parcel.allocated_departments()
        assert len(result) == 0
