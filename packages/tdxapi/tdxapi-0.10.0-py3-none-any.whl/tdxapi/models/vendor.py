import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.contact_information import ContactInformation
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class Vendor(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.Vendor"

    #: The ID of the vendor.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the vendor.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the vendor.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The name of the vendor.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the vendor.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The active status of the vendor.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The account number of the vendor used to represent the organization.
    account_number = attr.ib(default=None, metadata={"tdx_name": "AccountNumber"})

    #: The contract provider status of the vendor.
    is_contract_provider = attr.ib(
        default=None, metadata={"tdx_name": "IsContractProvider"}
    )

    #: The manufacturer status of the vendor.
    is_manufacturer = attr.ib(default=None, metadata={"tdx_name": "IsManufacturer"})

    #: The supplier status of the vendor.
    is_supplier = attr.ib(default=None, metadata={"tdx_name": "IsSupplier"})

    #: The contact information of the vendor's company.
    company_information = attr.ib(
        default=None,
        converter=ContactInformation.from_data,
        metadata={"tdx_name": "CompanyInformation"},
    )

    #: The name of the primary contact associated with the vendor.
    contact_name = attr.ib(default=None, metadata={"tdx_name": "ContactName"})

    #: The title of the primary contact associated with the vendor.
    contact_title = attr.ib(default=None, metadata={"tdx_name": "ContactTitle"})

    #: The department of the primary contact associated with the vendor.
    contact_department = attr.ib(
        default=None, metadata={"tdx_name": "ContactDepartment"}
    )

    #: The email address of the primary contact associated with the vendor.
    contact_email = attr.ib(default=None, metadata={"tdx_name": "ContactEmail"})

    #: The contact information of the vendor's primary contact.
    primary_contact_information = attr.ib(
        default=None,
        converter=ContactInformation.from_data,
        metadata={"tdx_name": "PrimaryContactInformation"},
    )

    #: The number of contracts provided by this vendor.
    contracts_count = attr.ib(default=None, metadata={"tdx_name": "ContractsCount"})

    #: The number of product models manufactured by this vendor.
    product_models_count = attr.ib(
        default=None, metadata={"tdx_name": "ProductModelsCount"}
    )

    #: The number of assets supplied by this vendor.
    assets_supplied_count = attr.ib(
        default=None, metadata={"tdx_name": "AssetsSuppliedCount"}
    )

    #: The custom attributes associated with the vendor.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The created date of the vendor.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the vendor.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the vendor.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the vendor.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the vendor.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the vendor.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )
