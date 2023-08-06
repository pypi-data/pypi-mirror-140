import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ConfigurationRelationshipTypeSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationRelationshipTypeSearch"

    #: The text to perform a LIKE search on the relationship type description and
    #: inverse description.
    description_like = attr.ib(default=None, metadata={"tdx_name": "DescriptionLike"})

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The operational dependency status to filter on.
    is_operational_dependency = attr.ib(
        default=None, metadata={"tdx_name": "IsOperationalDependency"}
    )
