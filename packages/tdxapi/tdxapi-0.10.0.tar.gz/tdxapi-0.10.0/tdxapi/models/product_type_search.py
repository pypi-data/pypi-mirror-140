import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ProductTypeSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.ProductTypeSearch"

    #: The search text to filter on. When set, results will be sorted by their text
    #: relevancy.
    search_text = attr.ib(default=None, metadata={"tdx_name": "SearchText"})

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The top-level status to filter on.
    is_top_level = attr.ib(default=None, metadata={"tdx_name": "IsTopLevel"})

    #: The parent product type ID to filter on. When set, only direct children of this
    #: type will be included.
    parent_product_type_id = attr.ib(
        default=None, metadata={"tdx_name": "ParentProductTypeID"}
    )
