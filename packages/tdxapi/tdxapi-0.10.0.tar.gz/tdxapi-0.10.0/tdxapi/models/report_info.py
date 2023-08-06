import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class ReportInfo(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.ReportInfo"

    #: The ID of the report.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the report.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The UID of the user who created the report.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the report.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The created date of the report.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The system name of the application containing the report.
    app_class = attr.ib(default=None, metadata={"tdx_name": "SystemAppName"})

    #: The ID of the platform application containing the report.
    app_id = attr.ib(default=None, metadata={"tdx_name": "PlatformAppID"})

    #: The name of the platform application containing the report.
    app_name = attr.ib(default=None, metadata={"tdx_name": "PlatformAppName"})

    #: The ID of the report source associated with the report.
    source_id = attr.ib(default=None, metadata={"tdx_name": "ReportSourceID"})

    #: The name of the report source associated with the report.
    source_name = attr.ib(default=None, metadata={"tdx_name": "ReportSourceName"})

    #: The URI to retrieve the full details of the report via the web API.
    uri = attr.ib(default=None, metadata={"tdx_name": "Uri"})
