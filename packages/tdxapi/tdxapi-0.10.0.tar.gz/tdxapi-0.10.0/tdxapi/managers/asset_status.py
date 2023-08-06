from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxAppMixin
from tdxapi.models.asset_status import AssetStatus
from tdxapi.models.asset_status_search import AssetStatusSearch


@attr.s
class AssetStatusManager(TdxManager, TdxAppMixin):
    @tdx_method("GET", "/api/{appId}/assets/statuses/{id}")
    def get(self, asset_status_id: int) -> AssetStatus:
        """Gets an asset status."""
        return self.dispatcher.send(
            self.get.method,
            self.get.url.format(appId=self.app_id, id=asset_status_id),
            rclass=AssetStatus,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("GET", "/api/{appId}/assets/statuses")
    def all(self) -> List[AssetStatus]:
        """Gets a list of all asset statuses."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url.format(appId=self.app_id),
            rclass=AssetStatus,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/{appId}/assets/statuses/search")
    def search(
        self,
        is_active: Optional[bool] = None,
        is_out_of_service: Optional[bool] = None,
        search_text: Optional[str] = None,
    ) -> List[AssetStatus]:
        """Gets a list of asset statuses.

        :param is_active: The active status to filter on.
        :param is_out_of_service: The "out of service" status to filter on.
        :param search_text: The search text to filter on. When set, results will be
            ordered by their text relevancy.
        """
        params = self._format_search_params(AssetStatusSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url.format(appId=self.app_id),
            data=params,
            rclass=AssetStatus,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> AssetStatus:
        """Generate new AssetStatus object."""
        return self._new(AssetStatus, **kwargs)

    def save(self, asset_status: AssetStatus, force: Optional[bool] = False) -> None:
        """Create or update an AssetStatus."""
        self._save(asset_status, force)

    @tdx_method("POST", "/api/{appId}/assets/statuses")
    def _create(self, asset_status: AssetStatus) -> AssetStatus:
        """Creates a new asset status."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(appId=self.app_id),
            data=asset_status,
            rclass=AssetStatus,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/{appId}/assets/statuses/{id}")
    def _update(self, asset_status: AssetStatus) -> AssetStatus:
        """Edits an existing asset status."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(appId=self.app_id, id=asset_status.id),
            data=asset_status,
            rclass=AssetStatus,
            rlist=False,
            rpartial=False,
        )
