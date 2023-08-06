from typing import Any, List, Optional, Tuple

import attr

from tdxapi.enums.component import Component
from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxCustomAttributeMixin
from tdxapi.models.location import Location
from tdxapi.models.location_search import LocationSearch


@attr.s
class LocationManager(TdxManager, TdxCustomAttributeMixin):
    __tdx_component__ = Component.LOCATION

    @tdx_method("GET", "/api/locations/{id}")
    def get(self, location_id: int) -> Location:
        """Gets a location."""
        location = self.dispatcher.send(
            self.get.method,
            self.get.url.format(id=location_id),
            rclass=Location,
            rlist=False,
            rpartial=False,
        )

        if location:
            location.attributes.match_template(self.attribute_template)

        return location

    @tdx_method("GET", "/api/locations")
    def all(self) -> List[Location]:
        """Gets a list of all active locations."""
        return self.dispatcher.send(
            self.all.method,
            self.all.url,
            rclass=Location,
            rlist=True,
            rpartial=True,
        )

    @tdx_method("POST", "/api/locations/search")
    def search(
        self,
        name_like: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_room_required: Optional[bool] = None,
        room_id: Optional[int] = None,
        return_item_counts: Optional[bool] = None,
        return_rooms: Optional[bool] = None,
        attributes: Optional[List[Tuple[int, Any]]] = None,
        max_results: Optional[int] = None,
    ) -> List[Location]:
        """Gets a list of locations.

        :param name_like: The text to perform a LIKE search on location name.
        :param is_active: The active status to filter on.
        :param is_room_required: The "room required" status to filter on.
        :param room_id: The location room ID to filter on.
        :param return_item_counts: Whether item counts should be returned for each
            location.
        :param return_rooms: Whether rooms should be returned for each location.
        :param attributes: The custom attributes to filter on.
        :param max_results: The maximum number of locations to return.
        """
        params = self._format_search_params(LocationSearch, locals())

        return self.dispatcher.send(
            self.search.method,
            self.search.url,
            data=params,
            rclass=Location,
            rlist=True,
            rpartial=True,
        )

    def new(self, **kwargs) -> Location:
        """Generate new Location object."""
        return self._new(Location, **kwargs)

    def save(self, location: Location, force: Optional[bool] = False) -> None:
        """Create or update a Location."""
        self._save(location, force)

    @tdx_method("POST", "/api/locations")
    def _create(self, location: Location) -> Location:
        """Creates a location."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url,
            data=location,
            rclass=Location,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/locations/{id}")
    def _update(self, location: Location) -> Location:
        """Edits the specified location."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(id=location.id),
            data=location,
            rclass=Location,
            rlist=False,
            rpartial=False,
        )
