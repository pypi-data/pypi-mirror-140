import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class ConfigurationItemSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationItemSearch"

    #: The name text to filter on.
    name_like = attr.ib(default=None, metadata={"tdx_name": "NameLike"})

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The configuration item type IDs to filter on.
    type_ids = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "TypeIDs"})

    #: The maintenance window IDs to filter on.
    maintenance_schedule_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "MaintenanceScheduleIDs"}
    )

    #: The custom attributes to filter on.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "CustomAttributes"},
    )
