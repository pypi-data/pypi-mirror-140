import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class OrderByColumn(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.OrderByColumn"

    #: The label of the column used to sort.
    label = attr.ib(default=None, metadata={"tdx_name": "ColumnLabel"})

    #: The name of the column used to sort.
    name = attr.ib(default=None, metadata={"tdx_name": "ColumnName"})

    #: Whether column uses ascending or descending order.
    is_ascending = attr.ib(default=None, metadata={"tdx_name": "IsAscending"})
