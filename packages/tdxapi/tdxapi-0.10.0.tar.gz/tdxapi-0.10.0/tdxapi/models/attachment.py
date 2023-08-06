import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class Attachment(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Attachments.Attachment"

    #: The ID of the attachment.
    id = attr.ib(default=None, converter=to_uid, metadata={"tdx_name": "ID"})

    #: The type of the attachment.
    type_id = attr.ib(default=None, metadata={"tdx_name": "AttachmentType"})

    #: The ID of the item associated with the attachment.
    item_id = attr.ib(default=None, metadata={"tdx_name": "ItemID"})

    #: The UID of the user who uploaded the attachment.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who uploaded the attachment.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The upload date of the attachment.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The file name of the attachment.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The size of the attachment, in bytes.
    size = attr.ib(default=None, metadata={"tdx_name": "Size"})

    #: The URI to retrieve the full details of the attachment via the web API.
    uri = attr.ib(default=None, metadata={"tdx_name": "Uri"})

    #: The URI to retrieve the contents of the attachment via the web API.
    content_uri = attr.ib(default=None, metadata={"tdx_name": "ContentUri"})

    #: The content of the attachment, or null if content is not being retrieved.
    content = attr.ib(default=None, repr=False, eq=False)
