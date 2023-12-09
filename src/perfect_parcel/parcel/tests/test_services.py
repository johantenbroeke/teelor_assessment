from io import StringIO

import pytest
from django.utils.dateparse import parse_datetime

from parcel.models import Container, Organisation, Parcel
from parcel.services import ContainerXMLParser


@pytest.fixture
def xml_data():
    return """
            <Container>
                <Id>123456</Id>
                <ShippingDate>2016-07-22T00:00:00+02:00</ShippingDate>
                <Parcel>
                    <Receipient>
                        <Name>John Doe</Name>
                        <Address>
                            <Street>Main Street</Street>
                            <HouseNumber>42</HouseNumber>
                            <PostalCode>12345</PostalCode>
                            <City>Eindhoven</City>
                        </Address>
                    </Receipient>
                    <Weight>2.5</Weight>
                    <Value>100.0</Value>
                </Parcel>
            </Container>
            """


@pytest.mark.django_db
def test_container_xml_parser(xml_data):
    # setup
    organisation = Organisation.objects.create(name="Test Organisation")
    xml_file = StringIO(xml_data)
    parser = ContainerXMLParser(xml_file, organisation)
    parser.parse()

    # get objects from the database
    container = Container.objects.get(id="123456")
    parcel = Parcel.objects.first()

    # assert
    assert container.shipping_date == parse_datetime("2016-07-22T00:00:00+02:00")
    assert container.organisation == organisation
    assert parcel.recipient_name == "John Doe"
    assert parcel.street == "Main Street"
