import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from parcel.models import Container, Organisation, Parcel, Rule


@pytest.fixture(name="xml_upload")
def xml_upload_fixture():
    xml_content = b"""<Container>
                      <Id>8520442</Id>
                      <ShippingDate>2023-12-08T11:25:22.795540</ShippingDate>
                      <parcels>
                        <Parcel>
                          <Receipient>
                            <Name>Recipient 1</Name>
                            <Address>
                              <Street>Street 1</Street>
                              <HouseNumber>88</HouseNumber>
                              <PostalCode>79906</PostalCode>
                              <City>City 1</City>
                            </Address>
                          </Receipient>
                          <Weight>93.39</Weight>
                          <Value>6762.14</Value>
                        </Parcel>
                        <Parcel>
                          <Receipient>
                            <Name>Recipient 2</Name>
                            <Address>
                              <Street>Street 2</Street>
                              <HouseNumber>61</HouseNumber>
                              <PostalCode>28632</PostalCode>
                              <City>City 2</City>
                            </Address>
                          </Receipient>
                          <Weight>92.51</Weight>
                          <Value>1235.96</Value>
                        </Parcel>
                        </parcels>
                    </Container>"""
    return xml_content


@pytest.fixture(name="user")
def user_fixture(client):
    # Create a test user and organisation
    user = User.objects.create_user(username="testuser", password="12345")
    organisation = Organisation.objects.create(name="Test Organisation")
    user.organisations.add(organisation)

    Rule.objects.create(organisation=organisation, python_code="pass", name="Rule 1")

    # Log in the test user
    client.login(username="testuser", password="12345")
    return user


@pytest.mark.django_db
class TestUploadXMLView:
    def test_get_upload_xml(self, client):
        url = reverse("upload_xml")
        response = client.get(url)
        assert response.status_code == 200

    def test_post_upload_xml(self, client, xml_upload, user):
        # Upload test XML file
        xml_file = SimpleUploadedFile("test.xml", xml_upload, content_type="text/xml")

        # POST the XML file
        url = reverse("upload_xml")
        response = client.post(url, {"file": xml_file}, follow=True)

        assert Container.objects.count() == 1
        assert Parcel.objects.count() == 2
        assert response.status_code == 200
        assert "XML File processed successfully" in response.content.decode()

    def test_post_invalid_upload_xml(self, client, user):
        # Create a test XML file
        xml_content = b"""<Container>BROKEN</Container>"""
        xml_file = SimpleUploadedFile("test.xml", xml_content, content_type="text/xml")

        # POST the XML file
        url = reverse("upload_xml")
        response = client.post(url, {"file": xml_file}, follow=True)

        assert Container.objects.count() == 0
        assert Parcel.objects.count() == 0
        assert response.status_code == 400
        assert "Error processing XML file" in response.content.decode()


@pytest.mark.django_db
class TestUserOrganisationParcelListView:
    def test_list_parcels(self, client, user, xml_upload):
        # Upload test XML file
        xml_file = SimpleUploadedFile("test.xml", xml_upload, content_type="text/xml")

        # POST the XML file
        url = reverse("upload_xml")
        response = client.post(url, {"file": xml_file}, follow=True)

        url = reverse("organisation_parcels")
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["parcels"]) == 2
