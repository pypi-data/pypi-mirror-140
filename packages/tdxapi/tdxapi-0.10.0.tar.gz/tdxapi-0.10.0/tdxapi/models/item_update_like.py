import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_uid


@attr.s(kw_only=True)
class ItemUpdateLike(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Feed.ItemUpdateLike"

    #: The ID of the like.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The full name of the user associated with the like.
    full_name = attr.ib(default=None, metadata={"tdx_name": "UserFullName"})

    #: The UID of the user associated with the like.
    uid = attr.ib(default=None, converter=to_uid, metadata={"tdx_name": "Uid"})
