import html
import re

import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.item_update_like import ItemUpdateLike
from tdxapi.models.item_update_reply import ItemUpdateReply
from tdxapi.models.participant import Participant


@attr.s(kw_only=True)
class ItemUpdate(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Feed.ItemUpdate"

    #: The ID of the feed entry.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The UID of the feed entry's creator.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The integer-based ID of the feed entry's creator.
    created_ref_id = attr.ib(default=None, metadata={"tdx_name": "CreatedRefID"})

    #: The full name of the feed entry's creator.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The first name of the feed entry's creator.
    created_first_name = attr.ib(
        default=None, metadata={"tdx_name": "CreatedFirstName"}
    )

    #: The last name of the feed entry's creator.
    created_last_name = attr.ib(default=None, metadata={"tdx_name": "CreatedLastName"})

    #: The profile image file path of the feed entry's creator.
    created_profile_image_file_name = attr.ib(
        default=None, metadata={"tdx_name": "CreatedByPicPath"}
    )

    #: The created date of the feed entry.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The last-modified date of the feed entry.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "LastUpdatedDate"}
    )

    #: The ID of the project/workspace/request associated with the feed entry.
    project_id = attr.ib(default=None, metadata={"tdx_name": "ProjectID"})

    #: The name of the project/workspace/request associated with the feed entry.
    project_name = attr.ib(default=None, metadata={"tdx_name": "ProjectName"})

    #: The ID of the parent item associated with the feed entry.
    plan_id = attr.ib(default=None, metadata={"tdx_name": "PlanID"})

    #: The name of the parent item associated with the feed entry.
    plan_name = attr.ib(default=None, metadata={"tdx_name": "PlanName"})

    #: The type of the item associated with the feed entry.
    item_type_id = attr.ib(default=None, metadata={"tdx_name": "ItemType"})

    #: The integer ID of the item associated with the feed entry.
    item_id = attr.ib(default=None, metadata={"tdx_name": "ItemID"})

    #: The title of the item associated with the feed entry.
    item_title = attr.ib(default=None, metadata={"tdx_name": "ItemTitle"})

    #: The GUID of the item associated with the feed entry.
    ref_id = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ReferenceID"}
    )

    #: The body of the feed entry.
    body = attr.ib(default=None, metadata={"tdx_name": "Body"})

    #: The update type of the feed entry.
    type_id = attr.ib(default=None, metadata={"tdx_name": "UpdateType"})

    #: The list of notified users associated with the feed entry.
    notified_list = attr.ib(default=None, metadata={"tdx_name": "NotifiedList"})

    #: The private status of the feed entry.
    is_private = attr.ib(default=None, metadata={"tdx_name": "IsPrivate"})

    #: Indicates if the feed entry is a parent of other feed entries.
    is_parent = attr.ib(default=None, metadata={"tdx_name": "IsParent"})

    #: The replies to the feed entry.
    replies = attr.ib(
        default=attr.Factory(list),
        converter=ItemUpdateReply.from_data,
        metadata={"tdx_name": "Replies"},
    )

    #: The number of replies to the feed entry.
    replies_count = attr.ib(default=None, metadata={"tdx_name": "RepliesCount"})

    #: The likes associated with the feed entry.
    likes = attr.ib(
        default=attr.Factory(list),
        converter=ItemUpdateLike.from_data,
        metadata={"tdx_name": "Likes"},
    )

    #: Indicates whether the user retrieving the feed entry has liked it.
    ilike = attr.ib(default=None, metadata={"tdx_name": "ILike"})

    #: The number of people who have liked the feed entry.
    likes_count = attr.ib(default=None, metadata={"tdx_name": "LikesCount"})

    #: The participants associated with the feed entry.
    participants = attr.ib(
        default=attr.Factory(list),
        converter=Participant.from_data,
        metadata={"tdx_name": "Participants"},
    )

    #: The breadcrumb HTML associated with the feed entry.
    breadcrumbs_html = attr.ib(default=None, metadata={"tdx_name": "BreadcrumbsHtml"})

    #: Not used.
    has_attachment = attr.ib(default=None, metadata={"tdx_name": "HasAttachment"})

    #: The URI to retrieve the full details of the feed entry via the web API.
    uri = attr.ib(default=None, metadata={"tdx_name": "Uri"})

    @property
    def body_text(self):
        # Remove HTML tags
        regex = re.compile("<.*?>")
        clean_text = re.sub(regex, "", self.body)

        # Return HTML decoded text with line breaks removed
        return " ".join(html.unescape(clean_text).split())
