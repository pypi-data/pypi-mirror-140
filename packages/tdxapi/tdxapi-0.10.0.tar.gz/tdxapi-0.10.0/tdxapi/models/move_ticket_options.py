import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class MoveTicketOptions(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Tickets.MoveTicketOptions"

    #: The ID of the ticketing application to move the ticket into.
    new_app_id = attr.ib(default=None, metadata={"tdx_name": "NewAppID"})

    #: The ID of the form in the destination ticketing application to assign to the
    #: moved ticket.
    new_form_id = attr.ib(default=None, metadata={"tdx_name": "NewFormID"})

    #: The ID of the ticket type in the destination ticketing application to assign to
    #: the moved ticket.
    new_ticket_type_id = attr.ib(default=None, metadata={"tdx_name": "NewTicketTypeID"})

    #: The ID of the status in the destination ticketing application to assign to the
    #: moved ticket.
    new_status_id = attr.ib(default=None, metadata={"tdx_name": "NewStatusID"})

    #: The comments of the move (ticket) to application feed entry.
    comments = attr.ib(default=None, metadata={"tdx_name": "Comments"})
