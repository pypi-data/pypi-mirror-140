import attr

from tdxapi.models.attachment import Attachment
from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class Asset(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.Asset"

    #: The ID of the asset.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the asset.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the asset.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The ID of the form associated with the asset. If a value of 0 is provided, then
    #: the default asset form for the associated application will be used.
    form_id = attr.ib(default=None, metadata={"tdx_name": "FormID"})

    #: The name of the form associated with the asset.
    form_name = attr.ib(default=None, metadata={"tdx_name": "FormName"})

    #: The ID of the product model associated with the asset.
    product_model_id = attr.ib(default=None, metadata={"tdx_name": "ProductModelID"})

    #: The name of the product model associated with the asset.
    product_model_name = attr.ib(
        default=None, metadata={"tdx_name": "ProductModelName"}
    )

    #: The ID of the manufacturer associated with the asset.
    manufacturer_id = attr.ib(default=None, metadata={"tdx_name": "ManufacturerID"})

    #: The name of the manufacturer associated with the asset.
    manufacturer_name = attr.ib(default=None, metadata={"tdx_name": "ManufacturerName"})

    #: The ID of the supplier associated with the asset.
    supplier_id = attr.ib(default=None, metadata={"tdx_name": "SupplierID"})

    #: The name of the supplier associated with the asset.
    supplier_name = attr.ib(default=None, metadata={"tdx_name": "SupplierName"})

    #: The ID of the status associated with the asset.
    status_id = attr.ib(default=None, metadata={"tdx_name": "StatusID"})

    #: The name of the status associated with the asset.
    status_name = attr.ib(default=None, metadata={"tdx_name": "StatusName"})

    #: The ID of the location associated with the asset.
    location_id = attr.ib(default=None, metadata={"tdx_name": "LocationID"})

    #: The name of the location associated with the asset.
    location_name = attr.ib(default=None, metadata={"tdx_name": "LocationName"})

    #: The ID of the location room associated with the asset.
    location_room_id = attr.ib(default=None, metadata={"tdx_name": "LocationRoomID"})

    #: The name of the location room associated with the asset.
    location_room_name = attr.ib(
        default=None, metadata={"tdx_name": "LocationRoomName"}
    )

    #: The service tag of the asset.
    service_tag = attr.ib(default=None, metadata={"tdx_name": "Tag"})

    #: The serial number of the asset.
    serial_number = attr.ib(default=None, metadata={"tdx_name": "SerialNumber"})

    #: The name of the asset.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The purchase cost of the asset.
    purchase_cost = attr.ib(default=None, metadata={"tdx_name": "PurchaseCost"})

    #: The acquisition date of the asset.
    acquisition_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "AcquisitionDate"}
    )

    #: The expected replacement date of the asset.
    expected_replacement_date = attr.ib(
        default=None,
        converter=to_datetime,
        metadata={"tdx_name": "ExpectedReplacementDate"},
    )

    #: The UID of the requesting user associated with the asset.
    requesting_customer_id = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "RequestingCustomerID"}
    )

    #: The name of the requesting user associated with the asset.
    requesting_customer_name = attr.ib(
        default=None, metadata={"tdx_name": "RequestingCustomerName"}
    )

    #: The ID of the requesting account/department associated with the asset.
    requesting_department_id = attr.ib(
        default=None, metadata={"tdx_name": "RequestingDepartmentID"}
    )

    #: The name of the requesting account/department associated with the asset.
    requesting_department_name = attr.ib(
        default=None, metadata={"tdx_name": "RequestingDepartmentName"}
    )

    #: The UID of the owning user associated with the asset.
    owning_customer_id = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "OwningCustomerID"}
    )

    #: The name of the owning user associated with the asset.
    owning_customer_name = attr.ib(
        default=None, metadata={"tdx_name": "OwningCustomerName"}
    )

    #: The ID of the owning account/department associated with the asset.
    owning_department_id = attr.ib(
        default=None, metadata={"tdx_name": "OwningDepartmentID"}
    )

    #: The name of the owning account/department associated with the asset.
    owning_department_name = attr.ib(
        default=None, metadata={"tdx_name": "OwningDepartmentName"}
    )

    #: The ID of the parent associated with the asset.
    parent_id = attr.ib(default=None, metadata={"tdx_name": "ParentID"})

    #: The serial number of the parent associated with the asset.
    parent_serial_number = attr.ib(
        default=None, metadata={"tdx_name": "ParentSerialNumber"}
    )

    #: The name of the parent associated with the asset.
    parent_name = attr.ib(default=None, metadata={"tdx_name": "ParentName"})

    #: The service tag of the parent associated with the asset.
    parent_service_tag = attr.ib(default=None, metadata={"tdx_name": "ParentTag"})

    #: The ID of the maintenance window associated with the asset.
    maintenance_schedule_id = attr.ib(
        default=None, metadata={"tdx_name": "MaintenanceScheduleID"}
    )

    #: The name of the maintenance window associated with the asset.
    maintenance_schedule_name = attr.ib(
        default=None, metadata={"tdx_name": "MaintenanceScheduleName"}
    )

    #: The ID of the configuration item record associated with the asset.
    configuration_item_id = attr.ib(
        default=None, metadata={"tdx_name": "ConfigurationItemID"}
    )

    #: The created date of the asset.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the asset.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the asset.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the asset.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the asset.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the asset.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )

    #: The external ID of the asset. This value is used to map the asset to its
    #: representation in external sources such as third-party CMDBs.
    external_id = attr.ib(default=None, metadata={"tdx_name": "ExternalID"})

    #: The ID of the configuration item source associated with the asset.
    external_source_id = attr.ib(
        default=None, metadata={"tdx_name": "ExternalSourceID"}
    )

    #: The name of the configuration item source associated with the asset.
    external_source_name = attr.ib(
        default=None, metadata={"tdx_name": "ExternalSourceName"}
    )

    #: The custom attributes associated with the asset. Since assets support custom
    #: forms, the IsRequired property is ignored. Alternatively, required status is
    #: driven by the form, which can be changed via the FormID property.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The attachments associated with the asset.
    attachments = attr.ib(
        default=attr.Factory(list),
        converter=Attachment.from_data,
        metadata={"tdx_name": "Attachments"},
    )

    #: The URI to retrieve the full details of the asset via the web API.
    uri = attr.ib(default=None, metadata={"tdx_name": "Uri"})
