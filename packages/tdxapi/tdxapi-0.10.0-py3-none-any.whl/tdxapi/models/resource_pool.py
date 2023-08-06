import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class ResourcePool(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Schedules.ResourcePool"

    #: The ID of the resource pool.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the resource pool.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The created date of the resource pool.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The last modified date of the resource pool.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The active status of the resource pool.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: Whether an email notification will be delivered to the manager when a resource
    #: in the pool is assigned.
    notify_on_assignment = attr.ib(
        default=None, metadata={"tdx_name": "NotifyOnAssignment"}
    )

    #: Whether the resource pool requires approval.
    requires_approval = attr.ib(default=None, metadata={"tdx_name": "RequiresApproval"})

    #: The full name of the user marked as the resource pool manager.
    manager_full_name = attr.ib(default=None, metadata={"tdx_name": "ManagerFullName"})

    #: The UID of the user marked as the resource pool manager.
    manager_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ManagerUID"}
    )

    #: The number of resources in the resource pool.
    resources_count = attr.ib(default=None, metadata={"tdx_name": "ResourceCount"})
