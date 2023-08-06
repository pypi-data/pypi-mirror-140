import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_uid


@attr.s(kw_only=True)
class ReportSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.ReportSearch"

    #: The UID of the report owner to filter on.
    owner_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "OwnerUid"}
    )

    #: The search text to filter on report names.
    search_text = attr.ib(default=None, metadata={"tdx_name": "SearchText"})

    #: The ID of the associated platform application to filter on.
    app_id = attr.ib(default=None, metadata={"tdx_name": "ForAppID"})

    #: The system name of the application to filter on.
    app_class = attr.ib(default=None, metadata={"tdx_name": "ForApplicationName"})

    #: The ID of the associated report source to filter on.
    source_id = attr.ib(default=None, metadata={"tdx_name": "ReportSourceID"})
