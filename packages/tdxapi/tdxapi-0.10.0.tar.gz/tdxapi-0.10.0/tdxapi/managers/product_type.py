from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxAppMixin
from tdxapi.models.product_type import ProductType
from tdxapi.models.product_type_search import ProductTypeSearch


@attr.s
class ProductTypeManager(TdxManager, TdxAppMixin):
    @tdx_method("GET", "/api/{appId}/assets/models/types/{id}")
    def get(self, product_type_id: int) -> ProductType:
        """Gets a product type."""
        return self.dispatcher.send(
            self.get.method,
            self.get.url.format(appId=self.app_id, id=product_type_id),
            rclass=ProductType,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("GET", "/api/{appId}/assets/models/types")
    def all(self) -> List[ProductType]:
        """Gets a list of all product types."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url.format(appId=self.app_id),
            rclass=ProductType,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/{appId}/assets/models/types/search")
    def search(
        self,
        search_text: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_top_level: Optional[bool] = None,
        parent_product_type_id: Optional[int] = None,
    ) -> List[ProductType]:
        """Gets a list of product types.

        :param search_text: The search text to filter on. When set, results will be
            sorted by their text relevancy.
        :param is_active: The active status to filter on.
        :param is_top_level: The top-level status to filter on.
        :param parent_product_type_id: The parent product type ID to filter on. When
            set, only direct children of this type will be included.
        """
        params = self._format_search_params(ProductTypeSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url.format(appId=self.app_id),
            data=params,
            rclass=ProductType,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> ProductType:
        """Generate new ProductType object."""
        return self._new(ProductType, **kwargs)

    def save(
        self,
        product_type: ProductType,
        on_update_cascade_status: Optional[bool] = False,
        force: Optional[bool] = False,
    ) -> None:
        """Create or update a ProductType.

        cascade_status only applies to ProductType updates.
        """
        if product_type.id:
            self._save(product_type, force, cascade_status=on_update_cascade_status)
        else:
            self._save(product_type, force)

    @tdx_method("POST", "/api/{appId}/assets/models/types")
    def _create(self, product_type: ProductType) -> ProductType:
        """Creates a new product type."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(appId=self.app_id),
            data=product_type,
            rclass=ProductType,
            rlist=False,
            rpartial=False,
        )

    @tdx_method(
        "PUT",
        "/api/{appId}/assets/models/types/{id}"
        "?cascadeActiveStatus={cascadeActiveStatus}",
    )
    def _update(
        self, product_type: ProductType, cascade_status: Optional[bool] = False
    ) -> ProductType:
        """Edits a product type."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(
                appId=self.app_id,
                id=product_type.id,
                cascadeActiveStatus=cascade_status,
            ),
            data=product_type,
            rclass=ProductType,
            rlist=False,
            rpartial=False,
        )
