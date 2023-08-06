import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class Application(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Apps.OrgApplication"

    #: The ID of the application.
    id = attr.ib(default=None, metadata={"tdx_name": "AppID"})

    #: The name of the application.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the application.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The type of the application. Types include Standard, Ticketing, Assets/CI,
    #: Client Portal, or External.
    type = attr.ib(default=None, metadata={"tdx_name": "Type"})

    #: The class of the application.
    app_class = attr.ib(default=None, metadata={"tdx_name": "AppClass"})

    #: The external URL of the application.
    external_url = attr.ib(default=None, metadata={"tdx_name": "ExternalUrl"})

    #: The purpose of the application.
    purpose = attr.ib(default=None, metadata={"tdx_name": "Purpose"})

    #: The active status of the application.
    is_active = attr.ib(default=None, metadata={"tdx_name": "Active"})

    #: The partial URL of the Client Portal application.
    partial_url = attr.ib(default=None, metadata={"tdx_name": "PartialUrl"})
