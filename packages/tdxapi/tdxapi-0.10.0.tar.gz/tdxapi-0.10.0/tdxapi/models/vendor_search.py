import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class VendorSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.VendorSearch"

    #: The text to perform a LIKE search on the vendor name.
    name_like = attr.ib(default=None, metadata={"tdx_name": "NameLike"})

    #: The search text to filter on. When set, this will sort the results by their text
    #: relevancy.
    search_text = attr.ib(default=None, metadata={"tdx_name": "SearchText"})

    #: Whether only vendors classified as product manufacturers should be returned.
    only_manufacturers = attr.ib(
        default=None, metadata={"tdx_name": "OnlyManufacturers"}
    )

    #: Whether only vendors classified as asset suppliers should be returned.
    only_suppliers = attr.ib(default=None, metadata={"tdx_name": "OnlySuppliers"})

    #: Whether only vendors classified as contract providers should be returned.
    only_contract_providers = attr.ib(
        default=None, metadata={"tdx_name": "OnlyContractProviders"}
    )

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The custom attributes to filter on.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "CustomAttributes"},
    )
