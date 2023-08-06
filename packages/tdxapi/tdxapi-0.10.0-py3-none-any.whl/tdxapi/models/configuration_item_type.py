import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class ConfigurationItemType(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationItemType"

    #: The ID of the configuration item type.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the asset/CI application containing the configuration item type.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the asset/CI application containing the configuration item type.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: Whether the item type is system-defined.
    is_system_defined = attr.ib(default=None, metadata={"tdx_name": "IsSystemDefined"})

    #: The name of the configuration item type.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The active status of the configuration item type.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The created date of the configuration item type.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDateUtc"}
    )

    #: The UID of the user who created the configuration item type.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the configuration item type.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the configuration item type.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDateUtc"}
    )

    #: The UID of the user who last modified the configuration item type.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the configuration item type.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )
