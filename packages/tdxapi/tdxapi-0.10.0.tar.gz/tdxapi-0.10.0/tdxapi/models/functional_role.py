import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime


@attr.s(kw_only=True)
class FunctionalRole(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Roles.FunctionalRole"

    #: The ID of the functional role.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the functional role.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The standard rate of the functional role.
    standard_rate = attr.ib(default=None, metadata={"tdx_name": "StandardRate"})

    #: The cost rate of the functional role.
    cost_rate = attr.ib(default=None, metadata={"tdx_name": "CostRate"})

    #: The created date of the functional role.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The last modified date of the functional role.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The comments of the functional role.
    comments = attr.ib(default=None, metadata={"tdx_name": "Comments"})

    #: The number of users associated with the functional role.
    users_count = attr.ib(default=None, metadata={"tdx_name": "UsersCount"})

    #: The number of requests associated with the functional role.
    requests_count = attr.ib(default=None, metadata={"tdx_name": "RequestsCount"})

    #: The number of projects associated with the functional role.
    projects_count = attr.ib(default=None, metadata={"tdx_name": "ProjectsCount"})

    #: The number of opportunities associated with the functional role.
    opportunities_count = attr.ib(
        default=None, metadata={"tdx_name": "OpportunitiesCount"}
    )

    #: The number of resource requests associated with the functional role.
    resource_requests_count = attr.ib(
        default=None, metadata={"tdx_name": "ResourceRequestsCount"}
    )
