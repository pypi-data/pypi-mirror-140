import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class Form(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Forms.Form"

    #: The ID of the form.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The name of the form.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The ID of the platform application containing the form.
    app_id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the platform application containing the form.
    app_name = attr.ib(default=None, metadata={"tdx_name": "AppName"})

    #: The ID of the component associated with the form.
    component_id = attr.ib(default=None, metadata={"tdx_name": "ComponentID"})

    #: The active status of the form.
    is_active = attr.ib(default=None, metadata={"tdx_name": "IsActive"})

    #: The configured status of the form.
    is_configured = attr.ib(default=None, metadata={"tdx_name": "IsConfigured"})

    #: The default status of the form.
    is_default = attr.ib(default=None, metadata={"tdx_name": "IsDefaultForApp"})

    #: The pinned status of the form. Currently only supported for tickets.
    is_pinned = attr.ib(default=None, metadata={"tdx_name": "IsPinned"})

    #: Whether the form should automatically expand help-text sections.
    should_expand_help = attr.ib(
        default=None, metadata={"tdx_name": "ShouldExpandHelp"}
    )

    #: The created date of the form.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDate"}
    )

    #: The UID of the user who created the form.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUid"}
    )

    #: The full name of the user who created the form.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})

    #: The last modified date of the form.
    modified_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ModifiedDate"}
    )

    #: The UID of the user who last modified the form.
    modified_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "ModifiedUid"}
    )

    #: The full name of the user who last modified the form.
    modified_full_name = attr.ib(
        default=None, metadata={"tdx_name": "ModifiedFullName"}
    )

    #: The number of assets associated with the form, or -1 if this total has not been
    #: loaded.
    assets_count = attr.ib(default=None, metadata={"tdx_name": "AssetsCount"})

    #: The number of configuration items associated with the form, or -1 if this total
    #: has not been loaded.
    configuration_items_count = attr.ib(
        default=None, metadata={"tdx_name": "ConfigurationItemsCount"}
    )
