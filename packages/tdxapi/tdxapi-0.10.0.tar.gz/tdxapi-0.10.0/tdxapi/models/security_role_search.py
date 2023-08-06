import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class SecurityRoleSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Roles.SecurityRoleSearch"

    #: The text to perform a LIKE search on security role name.
    name_like = attr.ib(default=None, metadata={"tdx_name": "NameLike"})

    #: The ID of the associated application to filter on.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The ID of the associated license type to filter on.
    license_type_id = attr.ib(default=None, metadata={"tdx_name": "LicenseTypeID"})
