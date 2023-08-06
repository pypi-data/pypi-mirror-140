import attr

from tdxapi.models.attachment import Attachment
from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class ConfigurationItem(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationItem"

    #: The ID of the configuration item.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the configuration item.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the configuration item.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The ID of the form associated with the configuration item.
    form_id = attr.ib(default=None, metadata={"tdx_name": "FormID"})

    #: The name of the form associated with the configuration item.
    form_name = attr.ib(default=None, metadata={"tdx_name": "FormName"})

    #: Whether the configuration item is maintained automatically by the system.
    is_system_defined = attr.ib(
        default=None, metadata={"tdx_name": "IsSystemMaintained"}
    )

    #: The ID of the underlying TeamDynamix item in the system that this configuration
    #: item represents.
    backing_item_id = attr.ib(default=None, metadata={"tdx_name": "BackingItemID"})

    #: The type of the underlying TeamDynamix item in the system that this
    #: configuration item represents.
    backing_item_type_id = attr.ib(
        default=None,
        metadata={"tdx_name": "BackingItemType"},
    )

    #: The name of the configuration item.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The ID of the type associated with the configuration item.
    type_id = attr.ib(default=None, metadata={"tdx_name": "TypeID"})

    #: The name of the type associated with the configuration item.
    type_name = attr.ib(default=None, metadata={"tdx_name": "TypeName"})

    #: The ID of the maintenance window associated with the configuration item.
    maintenance_schedule_id = attr.ib(
        default=None, metadata={"tdx_name": "MaintenanceScheduleID"}
    )

    #: The name of the maintenance window associated with the configuration item.
    maintenance_schedule_name = attr.ib(
        default=None, metadata={"tdx_name": "MaintenanceScheduleName"}
    )

    #: The UID of the owner associated with the configuration item.
    owner_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "OwnerUID"}
    )

    #: The full name of the owner associated with the configuration item.
    owner_full_name = attr.ib(default=None, metadata={"tdx_name": "OwnerFullName"})

    #: The ID of the owning acct/dept associated with the configuration item.
    owning_department_id = attr.ib(
        default=None, metadata={"tdx_name": "OwningDepartmentID"}
    )

    #: The name of the owning acct/dept associated with the configuration item.
    owning_department_name = attr.ib(
        default=None, metadata={"tdx_name": "OwningDepartmentName"}
    )

    #: The ID of the owning group associated with the configuration item.
    owning_group_id = attr.ib(default=None, metadata={"tdx_name": "OwningGroupID"})

    #: The name of the owning group associated with the configuration item.
    owning_group_name = attr.ib(default=None, metadata={"tdx_name": "OwningGroupName"})

    #: The ID of the location associated with the configuration item.
    location_id = attr.ib(default=None, metadata={"tdx_name": "LocationID"})

    #: The name of the location associated with the configuration item.
    location_name = attr.ib(default=None, metadata={"tdx_name": "LocationName"})

    #: The ID of the location room associated with the configuration item.
    location_room_id = attr.ib(default=None, metadata={"tdx_name": "LocationRoomID"})

    #: The name of the location room associated with the configuration item.
    location_room_name = attr.ib(
        default=None, metadata={"tdx_name": "LocationRoomName"}
    )

    #: The active status of the configuration item. This will default to true.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The created date of the configuration item.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDateUtc"}
    )

    #: The UID of the user who created the configuration item.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the configuration item.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the configuration item.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDateUtc"}
    )

    #: The UID of the user who last modified the configuration item.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who created the configuration item.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )

    #: The external ID of the configuration item. This value is used to map the
    #: configuration item to its representation in external sources such as third-party
    #: CMDBs.
    external_id = attr.ib(default=None, metadata={"tdx_name": "ExternalID"})

    #: The ID of the configuration item source associated with the configuration item.
    external_source_id = attr.ib(
        default=None, metadata={"tdx_name": "ExternalSourceID"}
    )

    #: The name of the configuration item source associated with the configuration
    #: item.
    external_source_name = attr.ib(
        default=None, metadata={"tdx_name": "ExternalSourceName"}
    )

    #: The custom attributes associated with the configuration item.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The attachments associated with the configuration item.
    attachments = attr.ib(
        default=attr.Factory(list),
        converter=Attachment.from_data,
        metadata={"tdx_name": "Attachments"},
    )

    #: The URI to retrieve the full details of the configuration item via the web API.
    uri = attr.ib(default=None, metadata={"tdx_name": "Uri"})
