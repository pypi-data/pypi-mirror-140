import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class TicketListing(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Tickets.TicketListing"

    #: The ID of the ticket.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The title of the ticket.
    title = attr.ib(default=None, metadata={"tdx_name": "Title"})

    #: The ID of the ticketing application associated with the ticket.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the ticketing application associated with the ticket.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The ID of the classification associated with the ticket.
    classification_id = attr.ib(default=None, metadata={"tdx_name": "ClassificationID"})

    #: The name of the classification associated with the ticket.
    classification_name = attr.ib(
        default=None, metadata={"tdx_name": "ClassificationName"}
    )

    #: The ID of the status associated with the ticket.
    status_id = attr.ib(default=None, metadata={"tdx_name": "StatusID"})

    #: The name of the status associated with the ticket.
    status_name = attr.ib(default=None, metadata={"tdx_name": "StatusName"})

    #: The ID of the account/department associated with the ticket.
    account_id = attr.ib(default=None, metadata={"tdx_name": "AccountID"})

    #: The name of the account/department associated with the ticket.
    account_name = attr.ib(default=None, metadata={"tdx_name": "AccountName"})

    #: The ID of the category associated with the ticket's type.
    type_category_id = attr.ib(default=None, metadata={"tdx_name": "TypeCategoryID"})

    #: The name of the category associated with the ticket's type.
    type_category_name = attr.ib(
        default=None, metadata={"tdx_name": "TypeCategoryName"}
    )

    #: The ID of the type associated with the ticket.
    type_id = attr.ib(default=None, metadata={"tdx_name": "TypeID"})

    #: The name of the type associated with the ticket.
    type_name = attr.ib(default=None, metadata={"tdx_name": "TypeName"})

    #: The UID of the user who created the ticket.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The created date of the ticket.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The full name of the user who created the ticket.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The UID of the user who last modified the ticket.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The last modified date of the ticket.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The full name of the user who last modified the ticket.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )

    #: The UID of the user who requested the ticket.
    contact_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ContactUid"}
    )

    #: The full name of the user who requested the ticket.
    contact_full_name = attr.ib(default=None, metadata={"tdx_name": "ContactFullName"})

    #: The start date of the ticket.
    start_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "StartDate"}
    )

    #: The end date of the ticket.
    end_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "EndDate"}
    )

    #: The "Respond By" deadline for the SLA associated with the ticket.
    respond_by_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "RespondByDate"}
    )

    #: The "Resolve By" deadline for the SLA associated with the ticket.
    resolve_by_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ResolveByDate"}
    )

    #: The "Goes Off Hold" of the ticket.
    goes_off_hold_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "GoesOffHoldDate"}
    )

    #: The archived status of the ticket.
    is_archived = attr.ib(default=None, metadata={"tdx_name": "IsArchived"})

    #: The ID of the priority associated with the ticket.
    priority_id = attr.ib(default=None, metadata={"tdx_name": "PriorityID"})

    #: The name of the priority associated with the ticket.
    priority_name = attr.ib(default=None, metadata={"tdx_name": "PriorityName"})

    #: The ID of the location associated with the ticket.
    location_id = attr.ib(default=None, metadata={"tdx_name": "LocationID"})

    #: The name of the location associated with the ticket.
    location_name = attr.ib(default=None, metadata={"tdx_name": "LocationName"})

    #: The ID of the location room associated with the ticket.
    location_room_id = attr.ib(default=None, metadata={"tdx_name": "LocationRoomID"})

    #: The name of the location room associated with the ticket.
    location_room_name = attr.ib(
        default=None, metadata={"tdx_name": "LocationRoomName"}
    )
