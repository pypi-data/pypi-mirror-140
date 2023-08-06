from typing import Optional

import attr

from tdxapi.enums.component import Component
from tdxapi.managers.bases import TdxManager, tdx_method
from tdxapi.managers.mixins import TdxCustomAttributeMixin
from tdxapi.models.location_room import LocationRoom


@attr.s
class LocationRoomManager(TdxManager, TdxCustomAttributeMixin):
    __tdx_component__ = Component.LOCATION_ROOM

    @tdx_method("GET", "/api/locations/{id}/rooms/{roomId}")
    def get(self, room_id: int, location_id: int) -> LocationRoom:
        """Gets a location room."""
        room = self.dispatcher.send(
            self.get.method,
            self.get.url.format(id=location_id, roomId=room_id),
            rclass=LocationRoom,
            rlist=False,
            rpartial=False,
        )

        if room:
            room.attributes.match_template(self.attribute_template)

        return room

    @tdx_method("DELETE", "/api/locations/{id}/rooms/{roomId}")
    def delete(self, room_id: int, location_id: int) -> None:
        """Deletes a room in a location."""
        self.dispatcher.send(
            self.delete.method,
            self.delete.url.format(id=location_id, roomId=room_id),
        )

    def new(self, **kwargs) -> LocationRoom:
        """Generate new LocationRoom object."""
        return self._new(LocationRoom, **kwargs)

    def save(
        self, room: LocationRoom, location_id: int, force: Optional[bool] = False
    ) -> None:
        """Create or update a LocationRoom."""
        self._save(room, force, location_id)

    @tdx_method("POST", "/api/locations/{id}/rooms")
    def _create(self, room: LocationRoom, location_id: int) -> LocationRoom:
        """Creates a room in a location."""
        return self.dispatcher.send(
            self._create.method,
            self._create.url.format(id=location_id),
            data=room,
            rclass=LocationRoom,
            rlist=False,
            rpartial=False,
        )

    @tdx_method("PUT", "/api/locations/{id}/rooms/{roomId}")
    def _update(self, room: LocationRoom, location_id: int) -> LocationRoom:
        """Edits the specified room in a location."""
        return self.dispatcher.send(
            self._update.method,
            self._update.url.format(id=location_id, roomId=room.id),
            data=room,
            rclass=LocationRoom,
            rlist=False,
            rpartial=False,
        )
