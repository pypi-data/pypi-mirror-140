import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class ProductModel(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.ProductModel"

    #: The ID of the product model.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the product model.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the product model.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The name of the product model.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the product model.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The active status of the product model.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The ID of the manufacturer associated with the product model.
    manufacturer_id = attr.ib(default=None, metadata={"tdx_name": "ManufacturerID"})

    #: The name of the manufacturer associated with the product model.
    manufacturer_name = attr.ib(default=None, metadata={"tdx_name": "ManufacturerName"})

    #: The ID of the product type associated with the product model.
    product_type_id = attr.ib(default=None, metadata={"tdx_name": "ProductTypeID"})

    #: The name of the product type associated with the product model.
    product_type_name = attr.ib(default=None, metadata={"tdx_name": "ProductTypeName"})

    #: The part number of the product model.
    part_number = attr.ib(default=None, metadata={"tdx_name": "PartNumber"})

    #: The custom attributes associated with the product model.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The created date of the product model.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the product model.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the product model.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the product model.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the product model.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the product model.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )
