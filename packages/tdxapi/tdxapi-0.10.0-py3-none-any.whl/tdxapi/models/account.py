import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class Account(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Accounts.Account"

    #: The ID of the account.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the account.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The ID of the parent associated with the account, or null if the account has no
    #: parent.
    parent_id = attr.ib(default=None, metadata={"tdx_name": "ParentID"})

    #: The name of the parent associated with the account, or null if the account has
    #: no parent.
    parent_name = attr.ib(default=None, metadata={"tdx_name": "ParentName"})

    #: The active status of the account.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The first address line of the account.
    address_line1 = attr.ib(default=None, metadata={"tdx_name": "Address1"})

    #: The second address line of the account.
    address_line2 = attr.ib(default=None, metadata={"tdx_name": "Address2"})

    #: The third address line of the account.
    address_line3 = attr.ib(default=None, metadata={"tdx_name": "Address3"})

    #: The fourth address line of the account.
    address_line4 = attr.ib(default=None, metadata={"tdx_name": "Address4"})

    #: The city of the account.
    city = attr.ib(default=None, metadata={"tdx_name": "City"})

    #: The state/province of the account.
    state_name = attr.ib(default=None, metadata={"tdx_name": "StateName"})

    #: The abbreviation of the state/province associated with the account.
    state_abbr = attr.ib(default=None, metadata={"tdx_name": "StateAbbr"})

    #: The postal code of the account.
    zip = attr.ib(default=None, metadata={"tdx_name": "PostalCode"})

    #: The country of the account.
    country = attr.ib(default=None, metadata={"tdx_name": "Country"})

    #: The phone number of the account.
    phone = attr.ib(default=None, metadata={"tdx_name": "Phone"})

    #: The fax number of the account.
    fax = attr.ib(default=None, metadata={"tdx_name": "Fax"})

    #: The website URL of the account.
    url = attr.ib(default=None, metadata={"tdx_name": "Url"})

    #: The notes for the account.
    notes = attr.ib(default=None, metadata={"tdx_name": "Notes"})

    #: The created date of the account.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The last modified date of the account.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The code for the account.
    code = attr.ib(default=None, metadata={"tdx_name": "Code"})

    #: The ID of the industry associated with the account.
    industry_id = attr.ib(default=None, metadata={"tdx_name": "IndustryID"})

    #: The name of the industry associated with the account.
    industry_name = attr.ib(default=None, metadata={"tdx_name": "IndustryName"})

    #: The UID of the manager for the account.
    manager_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ManagerUID"}
    )

    #: The full name of the manager for the account.
    manager_full_name = attr.ib(default=None, metadata={"tdx_name": "ManagerFullName"})

    #: The custom attributes of the account.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )
