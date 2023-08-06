from typing import List, Optional

import attr

from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxAppMixin
from tdxapi.models.configuration_relationship_type import ConfigurationRelationshipType
from tdxapi.models.configuration_relationship_type_search import (
    ConfigurationRelationshipTypeSearch,
)


@attr.s
class ConfigurationRelationshipTypeManager(TdxManager, TdxAppMixin):
    @tdx_method("GET", "/api/{appId}/cmdb/relationshiptypes/{id}")
    def get(self, relationship_type_id: int) -> ConfigurationRelationshipType:
        """Gets a relationship type."""
        return self.dispatcher.send(
            self.get.method,
            self.get.url.format(appId=self.app_id, id=relationship_type_id),
            rclass=ConfigurationRelationshipType,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("GET", "/api/{appId}/cmdb/relationshiptypes")
    def all(self) -> List[ConfigurationRelationshipType]:
        """Gets a list of all active relationship types."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url.format(appId=self.app_id),
            rclass=ConfigurationRelationshipType,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/{appId}/cmdb/relationshiptypes/search")
    def search(
        self,
        description_like: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_operational_dependency: Optional[bool] = None,
    ) -> List[ConfigurationRelationshipType]:
        """Gets a list of configuration relationship types.

        :param description_like: The text to perform a LIKE search on the relationship
            type description and inverse description.
        :param is_active: The active status to filter on.
        :param is_operational_dependency: The operational dependency status to filter
            on.
        """
        params = self._format_search_params(
            ConfigurationRelationshipTypeSearch, locals()
        )

        return self.dispatcher.send(
            self.search.method,
            self.search.url.format(appId=self.app_id),
            data=params,
            rclass=ConfigurationRelationshipType,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> ConfigurationRelationshipType:
        """Generate new ConfigurationRelationshipType object."""
        return self._new(ConfigurationRelationshipType, **kwargs)

    def save(
        self,
        relationship_type: ConfigurationRelationshipType,
        force: Optional[bool] = False,
    ) -> None:
        """Create or update a ConfigurationRelationshipType."""
        self._save(relationship_type, force)

    @tdx_method("POST", "/api/{appId}/cmdb/relationshiptypes")
    def _create(
        self, relationship_type: ConfigurationRelationshipType
    ) -> ConfigurationRelationshipType:
        """Creates a configuration relationship type."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(appId=self.app_id),
            data=relationship_type,
            rclass=ConfigurationRelationshipType,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/{appId}/cmdb/relationshiptypes/{id}")
    def _update(
        self, relationship_type: ConfigurationRelationshipType
    ) -> ConfigurationRelationshipType:
        """Edits an existing configuration relationship type."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(appId=self.app_id, id=relationship_type.id),
            data=relationship_type,
            rclass=ConfigurationRelationshipType,
            rlist=False,
            rpartial=False,
        )
