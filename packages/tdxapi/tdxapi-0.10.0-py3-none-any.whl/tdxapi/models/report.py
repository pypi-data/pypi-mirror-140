import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.chart_setting import ChartSetting
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.display_column import DisplayColumn
from tdxapi.models.order_by_column import OrderByColumn


@attr.s(kw_only=True)
class Report(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.Report"

    #: The description of the report.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The maximum number of results that can be returned by the report.
    max_results = attr.ib(default=None, metadata={"tdx_name": "MaxResults"})

    #: The columns displayed in the report.
    columns = attr.ib(
        default=attr.Factory(list),
        converter=DisplayColumn.from_data,
        metadata={"tdx_name": "DisplayedColumns"},
    )

    #: The columns used to sort the rows in the report.
    sort_column = attr.ib(
        default=attr.Factory(list),
        converter=OrderByColumn.from_data,
        metadata={"tdx_name": "SortOrder"},
    )

    #: The type of the chart/graph that is configured for the report.
    chart_type = attr.ib(default=None, metadata={"tdx_name": "ChartType"})

    #: The chart settings associated with the report.
    chart_columns = attr.ib(
        default=attr.Factory(list),
        converter=ChartSetting.from_data,
        metadata={"tdx_name": "ChartSettings"},
    )

    #: The rows of data retrieved for the report.
    data = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "DataRows"})

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
