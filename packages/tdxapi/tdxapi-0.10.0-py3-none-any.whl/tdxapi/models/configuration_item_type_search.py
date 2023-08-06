import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ConfigurationItemTypeSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationItemTypeSearch"

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: Whether organizationally-defined types will be returned.
    is_system_defined = attr.ib(
        default=None, metadata={"tdx_name": "IsOrganizationallyDefined"}
    )

    #: The search text to filter on. When set, results will be ordered by their text
    #: relevancy.
    search_text = attr.ib(default=None, metadata={"tdx_name": "SearchText"})
