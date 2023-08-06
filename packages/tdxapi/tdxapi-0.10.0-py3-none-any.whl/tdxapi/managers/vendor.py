from typing import Any, List, Optional, Tuple

import attr

from tdxapi.enums.component import Component
from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxAppMixin, TdxCustomAttributeMixin
from tdxapi.models.vendor import Vendor
from tdxapi.models.vendor_search import VendorSearch


@attr.s
class VendorManager(TdxManager, TdxAppMixin, TdxCustomAttributeMixin):
    __tdx_component__ = Component.VENDOR

    @tdx_method("GET", "/api/{appId}/assets/vendors/{id}")
    def get(self, vendor_id: int) -> Vendor:
        """Gets a vendor."""
        vendor = self.dispatcher.send(
            self.get.method,
            self.get.url.format(appId=self.app_id, id=vendor_id),
            rclass=Vendor,
            rlist=False,
            rpartial=False,
        )

        if vendor:
            vendor.attributes.match_template(self.attribute_template)

        return vendor

    @tdx_method("GET", "/api/{appId}/assets/vendors")
    def all(self) -> List[Vendor]:  # noqa: A003
        """Gets a list of all active vendors."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url.format(appId=self.app_id),
            rclass=Vendor,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/{appId}/assets/vendors/search")
    def search(
        self,
        name_like: Optional[str] = None,
        search_text: Optional[str] = None,
        only_manufacturers: Optional[bool] = None,
        only_suppliers: Optional[bool] = None,
        only_contract_providers: Optional[bool] = None,
        is_active: Optional[bool] = None,
        attributes: Optional[List[Tuple[int, Any]]] = None,
    ) -> List[Vendor]:
        """Gets a list of vendors.

        :param name_like: The text to perform a LIKE search on the vendor name.
        :param search_text: The search text to filter on. When set, this will sort the
            results by their text relevancy.
        :param only_manufacturers: Whether only vendors classified as product
            manufacturers should be returned.
        :param only_suppliers: Whether only vendors classified as asset suppliers should
            be returned.
        :param only_contract_providers: Whether only vendors classified as contract
            providers should be returned.
        :param is_active: The active status to filter on.
        :param attributes: The custom attributes to filter on.
        """
        params = self._format_search_params(VendorSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url.format(appId=self.app_id),
            data=params,
            rclass=Vendor,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> Vendor:
        """Generate new Vendor object."""
        return self._new(Vendor, **kwargs)

    def save(self, vendor: Vendor, force: Optional[bool] = False) -> None:
        """Create or update a Vendor."""
        self._save(vendor, force)

    @tdx_method("POST", "/api/{appId}/assets/vendors")
    def _create(self, vendor: Vendor) -> Vendor:
        """Creates a new vendor."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(appId=self.app_id),
            data=vendor,
            rclass=Vendor,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/{appId}/assets/vendors/{id}")
    def _update(self, vendor: Vendor) -> Vendor:
        """Edits the vendor specified by the vendor ID."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(appId=self.app_id, id=vendor.id),
            data=vendor,
            rclass=Vendor,
            rlist=False,
            rpartial=False,
        )
