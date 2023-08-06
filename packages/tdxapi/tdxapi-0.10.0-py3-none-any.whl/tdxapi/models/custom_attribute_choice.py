import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime


@attr.s(kw_only=True)
class CustomAttributeChoice(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.CustomAttributes.CustomAttributeChoice"

    #: The ID of the attribute choice.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the attribute choice. This doubles as the display text for the
    #: choice.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The active status of the attribute choice.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The created date of the attribute choice.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "DateCreated"}
    )

    #: The last modified date of the attribute choice.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "DateModified"}
    )

    #: The order of the attribute choice in the list. Choices are first sorted by order
    #: (ascending) and their name (also ascending).
    order = attr.ib(default=None, metadata={"tdx_name": "Order"})
