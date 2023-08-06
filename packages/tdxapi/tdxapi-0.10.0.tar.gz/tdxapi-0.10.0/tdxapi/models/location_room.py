import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class LocationRoom(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Locations.LocationRoom"

    #: The ID of the location room.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the location room.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The external ID of the location room.
    external_id = attr.ib(default=None, metadata={"tdx_name": "ExternalID"})

    #: The description of the location room.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The floor information associated with the location room.
    floor = attr.ib(default=None, metadata={"tdx_name": "Floor"})

    #: The capacity of the location room.
    capacity = attr.ib(default=None, metadata={"tdx_name": "Capacity"})

    #: The number of assets associated with the location room.
    assets_count = attr.ib(default=None, metadata={"tdx_name": "AssetsCount"})

    #: The number of standalone configuration items associated with the location room.
    configuration_items_count = attr.ib(
        default=None, metadata={"tdx_name": "ConfigurationItemsCount"}
    )

    #: The number of tickets associated with the location room.
    tickets_count = attr.ib(default=None, metadata={"tdx_name": "TicketsCount"})

    #: The number of users associated with the location room.
    users_count = attr.ib(default=None, metadata={"tdx_name": "UsersCount"})

    #: The created date of the location room.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the location room.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUID"}
    )

    #: The full name of the user who created the location room.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The custom attributes associated with the location room.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "Attributes"},
    )
