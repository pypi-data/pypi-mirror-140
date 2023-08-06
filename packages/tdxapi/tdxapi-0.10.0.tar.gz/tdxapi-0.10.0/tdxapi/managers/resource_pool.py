from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.models.resource_pool import ResourcePool
from tdxapi.models.resource_pool_search import ResourcePoolSearch


@attr.s
class ResourcePoolManager(TdxManager):
    def get(self, resource_pool_id: int) -> ResourcePool:
        """Gets a ResourcePool."""
        for resource_pool in self.search():
            if resource_pool.id == resource_pool_id:
                return resource_pool

    @tdx_method("POST", "/api/resourcepools/search")
    def search(
        self,
        name_like: Optional[str] = None,
        manager_uid: Optional[str] = None,
        max_results: Optional[int] = None,
        is_active: Optional[bool] = None,
        return_item_counts: Optional[bool] = None,
    ) -> List[ResourcePool]:
        """Gets a list of resource pools.

        :param name_like: The resource pool name to filter on.
        :param manager_uid: The UID of the resource pool manager to filter on.
        :param max_results: The maximum number of results to return.
        :param is_active: The active status to filter on.
        :param return_item_counts: Whether resource counts should be retrieved for each
            pool. Defaults to false.
        """
        params = self._format_search_params(ResourcePoolSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url,
            data=params,
            rclass=ResourcePool,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> ResourcePool:
        """Generate new ResourcePool object."""
        return self._new(ResourcePool, **kwargs)

    def save(self, resource_pool: ResourcePool, force: Optional[bool] = False) -> None:
        """Create or update a ResourcePool."""
        self._save(resource_pool, force)

    @tdx_method("POST", "/api/resourcepools")
    def _create(self, resource_pool: ResourcePool) -> ResourcePool:
        """Creates a resource pool."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url,
            data=resource_pool,
            rclass=ResourcePool,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/resourcepools/{id}")
    def _update(self, resource_pool: ResourcePool) -> ResourcePool:
        """Edits the specified resource pool."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(id=resource_pool.id),
            data=resource_pool,
            rclass=ResourcePool,
            rlist=False,
            rpartial=False,
        )
