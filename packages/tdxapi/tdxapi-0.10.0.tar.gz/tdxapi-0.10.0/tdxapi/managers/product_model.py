from typing import Any, List, Optional, Tuple

import attr

from tdxapi.enums.component import Component
from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxAppMixin, TdxCustomAttributeMixin
from tdxapi.models.product_model import ProductModel
from tdxapi.models.product_model_search import ProductModelSearch


@attr.s
class ProductModelManager(TdxManager, TdxAppMixin, TdxCustomAttributeMixin):
    __tdx_component__ = Component.PRODUCT_MODEL

    @tdx_method("GET", "/api/{appId}/assets/models/{id}")
    def get(self, product_model_id: int) -> ProductModel:
        """Gets the specified product model."""
        product_model = self.dispatcher.send(
            self.get.method,
            self.get.url.format(appId=self.app_id, id=product_model_id),
            rclass=ProductModel,
            rlist=False,
            rpartial=False,
        )

        if product_model:
            product_model.attributes.match_template(self.attribute_template)

        return product_model

    @tdx_method("GET", "/api/{appId}/assets/models")
    def all(self) -> List[ProductModel]:
        """Gets a list of all active product models."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url.format(appId=self.app_id),
            rclass=ProductModel,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/{appId}/assets/models/search")
    def search(
        self,
        search_text: Optional[str] = None,
        manufacturer_id: Optional[int] = None,
        product_type_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        attributes: Optional[List[Tuple[int, Any]]] = None,
    ) -> List[ProductModel]:
        """Gets a list of product models.

        :param search_text: The search text to filter on. When set, the results will be
            sorted by their text relevancy.
        :param manufacturer_id: The ID of the manufacturer to filter on.
        :param product_type_id: The ID of the product type to filter on. This will NOT
            filter on product subtypes.
        :param is_active: The active status to filter on.
        :param attributes: The custom attributes to filter on.
        """
        params = self._format_search_params(ProductModelSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url.format(appId=self.app_id),
            data=params,
            rclass=ProductModel,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> ProductModel:
        """Generate new ProductModel object."""
        return self._new(ProductModel, **kwargs)

    def save(self, product_model: ProductModel, force: Optional[bool] = False) -> None:
        """Create or update a ProductModel."""
        self._save(product_model, force)

    @tdx_method("POST", "/api/{appId}/assets/models")
    def _create(self, product_model: ProductModel) -> ProductModel:
        """Creates a new product model."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(appId=self.app_id),
            data=product_model,
            rclass=ProductModel,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/{appId}/assets/models/{id}")
    def _update(self, product_model: ProductModel) -> ProductModel:
        """Edits the specified product model."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(appId=self.app_id, id=product_model.id),
            data=product_model,
            rclass=ProductModel,
            rlist=False,
            rpartial=False,
        )
