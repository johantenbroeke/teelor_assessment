from xml.dom import minidom

from django.utils.dateparse import parse_datetime

from .models import Container, Parcel


class ContainerXMLParser(object):
    """Parse a container XML file and create the corresponding objects"""

    def __init__(self, xml, organisation):
        self.xml = xml
        self.organisation = organisation

    def parse(self):
        dom = minidom.parse(self.xml)
        for container in dom.getElementsByTagName("Container"):
            container_id = container.getElementsByTagName("Id")[0].firstChild.data
            shipping_date = parse_datetime(
                container.getElementsByTagName("ShippingDate")[0].firstChild.data
            )

            container_obj = Container.objects.create(
                id=container_id,
                # shipping_date=timezone.make_aware(shipping_date),
                shipping_date=shipping_date,
                organisation=self.organisation,
            )

            for parcel in container.getElementsByTagName("Parcel"):
                recipient = parcel.getElementsByTagName("Receipient")[0]
                recipient_name = recipient.getElementsByTagName("Name")[
                    0
                ].firstChild.data
                address = recipient.getElementsByTagName("Address")[0]
                street = address.getElementsByTagName("Street")[0].firstChild.data
                house_number = address.getElementsByTagName("HouseNumber")[
                    0
                ].firstChild.data
                postal_code = address.getElementsByTagName("PostalCode")[
                    0
                ].firstChild.data
                city = address.getElementsByTagName("City")[0].firstChild.data
                weight = parcel.getElementsByTagName("Weight")[0].firstChild.data
                value = parcel.getElementsByTagName("Value")[0].firstChild.data

                Parcel.objects.create(
                    container=container_obj,
                    recipient_name=recipient_name,
                    street=street,
                    house_number=house_number,
                    postal_code=postal_code,
                    city=city,
                    weight=weight,
                    value=value,
                )
