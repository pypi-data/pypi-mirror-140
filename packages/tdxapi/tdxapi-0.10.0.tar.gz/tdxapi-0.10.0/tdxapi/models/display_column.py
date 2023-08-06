import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class DisplayColumn(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Reporting.DisplayColumn"

    #: The header text of the column.
    header_text = attr.ib(default=None, metadata={"tdx_name": "HeaderText"})

    #: The name of the column.
    column_name = attr.ib(default=None, metadata={"tdx_name": "ColumnName"})

    #: The data type of the column.
    data_type_id = attr.ib(default=None, metadata={"tdx_name": "DataType"})

    #: The full expression for sorting (including direction).
    sort_column_expression = attr.ib(
        default=None, metadata={"tdx_name": "SortColumnExpression"}
    )

    #: The name of the column used to sort.
    sort_column_name = attr.ib(default=None, metadata={"tdx_name": "SortColumnName"})

    #: The type of data in the column used to sort.
    sort_column_data_type_id = attr.ib(
        default=None, metadata={"tdx_name": "SortDataType"}
    )

    #: The aggregate function being applied to calculate this column.
    aggregate_function_id = attr.ib(default=None, metadata={"tdx_name": "Aggregate"})

    #: The component function being applied to this column.
    component_function_id = attr.ib(default=None, metadata={"tdx_name": "Component"})

    #: The expression used to calculate the column's footer.
    footer_expression = attr.ib(default=None, metadata={"tdx_name": "FooterExpression"})
