import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ChartSetting(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.ChartSetting"

    #: The axis represented by the setting.
    axis = attr.ib(default=None, metadata={"tdx_name": "Axis"})

    #: The label describing the column used for the setting.
    label = attr.ib(default=None, metadata={"tdx_name": "ColumnLabel"})

    #: The name of the column used for the setting.
    name = attr.ib(default=None, metadata={"tdx_name": "ColumnName"})
