import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class ItemUpdateReply(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Feed.ItemUpdateReply"

    #: The ID of the reply.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The body of the reply.
    body = attr.ib(default=None, metadata={"tdx_name": "Body"})

    #: The UID of the reply's creator.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The integer-based ID of the reply's creator.
    created_ref_id = attr.ib(default=None, metadata={"tdx_name": "CreatedRefID"})

    #: The full name of the reply's creator.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The first name of the reply's creator.
    created_first_name = attr.ib(
        default=None, metadata={"tdx_name": "CreatedFirstName"}
    )

    #: The last name of the the reply's creator.
    created_last_name = attr.ib(default=None, metadata={"tdx_name": "CreatedLastName"})

    #: The profile image file path of the reply's creator.
    created_profile_image_file_name = attr.ib(
        default=None, metadata={"tdx_name": "CreatedByPicPath"}
    )

    #: The created date of the reply.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )
