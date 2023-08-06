import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class SecurityRole(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Roles.SecurityRole"

    #: The ID of the security role.
    id = attr.ib(default=None, converter=to_uid, metadata={"tdx_name": "ID"})

    #: The name of the security role.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The created date of the security role.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The last modified date of the security role.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The number of users associated with the security role.
    users_count = attr.ib(default=None, metadata={"tdx_name": "UserCount"})

    #: The ID of the platform application containing the security role.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The permissions granted to users with this security role.
    permissions = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "Permissions"}
    )

    #: The license type associated with the security role.
    license_type_id = attr.ib(default=None, metadata={"tdx_name": "LicenseType"})

    #: The name of the license type associated with the security role.
    license_type_name = attr.ib(default=None, metadata={"tdx_name": "LicenseTypeName"})
