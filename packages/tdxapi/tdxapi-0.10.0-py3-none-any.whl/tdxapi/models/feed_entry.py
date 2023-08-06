import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class FeedEntry(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Feed.FeedEntry"

    #: The comments of the feed entry.
    comments = attr.ib(default=None, metadata={"tdx_name": "Comments"})

    #: The email addresses to notify associated with the feed entry.
    notify = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "Notify"})

    #: The private status of the feed entry.
    is_private = attr.ib(default=None, metadata={"tdx_name": "IsPrivate"})
