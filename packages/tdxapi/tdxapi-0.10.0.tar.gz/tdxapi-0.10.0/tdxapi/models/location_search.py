import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class LocationSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Locations.LocationSearch"

    #: The text to perform a LIKE search on location name.
    name_like = attr.ib(default=None, metadata={"tdx_name": "NameLike"})

    #: The active status to filter on.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The "room required" status to filter on.
    is_room_required = attr.ib(default=None, metadata={"tdx_name": "IsRoomRequired"})

    #: The location room ID to filter on.
    room_id = attr.ib(default=None, metadata={"tdx_name": "RoomID"})

    #: Whether item counts should be returned for each location.
    return_item_counts = attr.ib(
        default=None, metadata={"tdx_name": "ReturnItemCounts"}
    )

    #: Whether rooms should be returned for each location.
    return_rooms = attr.ib(default=None, metadata={"tdx_name": "ReturnRooms"})

    #: The custom attributes to filter on.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The maximum number of locations to return.
    max_results = attr.ib(default=0, metadata={"tdx_name": "MaxResults"})
