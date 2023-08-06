import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ContactInformation(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.ContactInformation"

    #: The ID of the contact information.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The first address line of the contact information.
    address_line1 = attr.ib(default=None, metadata={"tdx_name": "AddressLine1"})

    #: The second address line of the contact information.
    address_line2 = attr.ib(default=None, metadata={"tdx_name": "AddressLine2"})

    #: The third address line of the contact information.
    address_line3 = attr.ib(default=None, metadata={"tdx_name": "AddressLine3"})

    #: The fourth address line of the contact information.
    address_line4 = attr.ib(default=None, metadata={"tdx_name": "AddressLine4"})

    #: The city of the contact information.
    city = attr.ib(default=None, metadata={"tdx_name": "City"})

    #: The state/province of the contact information.
    state = attr.ib(default=None, metadata={"tdx_name": "State"})

    #: The postal code of the contact information.
    zip = attr.ib(default=None, metadata={"tdx_name": "PostalCode"})

    #: The country of the contact information.
    country = attr.ib(default=None, metadata={"tdx_name": "Country"})

    #: The URL of the contact information.
    url = attr.ib(default=None, metadata={"tdx_name": "Url"})

    #: The phone number of the contact information.
    phone = attr.ib(default=None, metadata={"tdx_name": "Phone"})

    #: The fax number of the contact information.
    fax = attr.ib(default=None, metadata={"tdx_name": "Fax"})
