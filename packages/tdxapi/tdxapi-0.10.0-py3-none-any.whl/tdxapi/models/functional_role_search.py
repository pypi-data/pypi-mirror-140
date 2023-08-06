import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class FunctionalRoleSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Roles.FunctionalRoleSearch"

    #: The name to filter on.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The maximum number of results to return.
    max_results = attr.ib(default=0, metadata={"tdx_name": "MaxResults"})

    #: Whether associated item counts should be returned.
    return_item_counts = attr.ib(
        default=None, metadata={"tdx_name": "ReturnItemCounts"}
    )
