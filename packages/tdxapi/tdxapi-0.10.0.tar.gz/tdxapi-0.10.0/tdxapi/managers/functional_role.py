from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.models.functional_role import FunctionalRole
from tdxapi.models.functional_role_search import FunctionalRoleSearch


@attr.s
class FunctionalRoleManager(TdxManager):
    def get(self, functional_role_id: int) -> FunctionalRole:
        """Gets a FunctionalRole."""
        for functional_role in self.search():
            if functional_role.id == functional_role_id:
                return functional_role

    @tdx_method("POST", "/api/functionalroles/search")
    def search(
        self,
        name: Optional[str] = None,
        max_results: Optional[int] = None,
        return_item_counts: Optional[bool] = None,
    ) -> List[FunctionalRole]:
        """Gets a list of functional roles.

        :param name: The name to filter on.
        :param max_results: The maximum number of results to return.
        :param return_item_counts: Whether associated item counts should be returned.
        """
        params = self._format_search_params(FunctionalRoleSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url,
            data=params,
            rclass=FunctionalRole,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> FunctionalRole:
        """Generate new FunctionalRole object."""
        return self._new(FunctionalRole, **kwargs)

    def save(
        self, functional_role: FunctionalRole, force: Optional[bool] = False
    ) -> None:
        """Create or update a FunctionalRole."""
        self._save(functional_role, force)

    @tdx_method("POST", "/api/functionalroles")
    def _create(self, functional_role: FunctionalRole) -> FunctionalRole:
        """Creates a functional role."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url,
            data=functional_role,
            rclass=FunctionalRole,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/functionalroles/{id}")
    def _update(self, functional_role: FunctionalRole) -> FunctionalRole:
        """Edits the specified functional role."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(id=functional_role.id),
            data=functional_role,
            rclass=FunctionalRole,
            rlist=False,
            rpartial=False,
        )
