import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList
from tdxapi.models.location_room import LocationRoom


@attr.s(kw_only=True)
class Location(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Locations.Location"

    #: The ID of the location.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the location.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the location.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The external ID of the location.
    external_id = attr.ib(default=None, metadata={"tdx_name": "ExternalID"})

    #: The active status of the location.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The address of the location.
    address = attr.ib(default=None, metadata={"tdx_name": "Address"})

    #: The city of the location.
    city = attr.ib(default=None, metadata={"tdx_name": "City"})

    #: The state/province of the location.
    state = attr.ib(default=None, metadata={"tdx_name": "State"})

    #: The postal code of the location.
    zip = attr.ib(default=None, metadata={"tdx_name": "PostalCode"})

    #: The country of the location.
    country = attr.ib(default=None, metadata={"tdx_name": "Country"})

    #: Whether the location requires a room when specified for an asset.
    is_room_required = attr.ib(default=None, metadata={"tdx_name": "IsRoomRequired"})

    #: The custom attributes associated with the location.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )

    #: The number of assets associated with the location.
    assets_count = attr.ib(default=None, metadata={"tdx_name": "AssetsCount"})

    #: The number of standalone configuration items associated with the location.
    configuration_items_count = attr.ib(
        default=None, metadata={"tdx_name": "ConfigurationItemsCount"}
    )

    #: The number of tickets associated with the location.
    tickets_count = attr.ib(default=None, metadata={"tdx_name": "TicketsCount"})

    #: The number of rooms associated with the location.
    rooms_count = attr.ib(default=None, metadata={"tdx_name": "RoomsCount"})

    #: The number of users associated with the location.
    users_count = attr.ib(default=None, metadata={"tdx_name": "UsersCount"})

    #: The rooms associated with the location. The custom attributes for each room will
    #: not be retrieved.
    rooms = attr.ib(
        default=attr.Factory(list),
        converter=LocationRoom.from_data,
        metadata={"tdx_name": "Rooms"},
    )

    #: The created date of the location.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the location.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the location.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the location.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the location.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the location.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )

    #: The latitude of the location.
    latitude = attr.ib(default=None, metadata={"tdx_name": "Latitude"})

    #: The longitude of the location.
    longitude = attr.ib(default=None, metadata={"tdx_name": "Longitude"})
