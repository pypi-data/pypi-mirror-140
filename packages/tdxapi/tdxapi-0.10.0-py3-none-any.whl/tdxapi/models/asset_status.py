import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class AssetStatus(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.AssetStatus"

    #: The ID of the asset status.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the asset status.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the asset status.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The name of the asset status.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the asset status.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The order of the asset status in a list.
    order = attr.ib(default=None, metadata={"tdx_name": "Order"})

    #: The active status of the asset status.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: Whether the asset status denotes that an associated asset is "out-of-service".
    is_out_of_service = attr.ib(default=None, metadata={"tdx_name": "IsOutOfService"})

    #: The created date of the asset status.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the asset status.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the asset status.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the asset status.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the asset status.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the asset status.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )
