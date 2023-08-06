import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class Permission(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Roles.Permission"

    #: The ID of the permission.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The short name of the permission.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The description of the permission.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The ID of the section associated with the permission.
    section_id = attr.ib(default=None, metadata={"tdx_name": "SectionID"})

    #: The name of the section associated with the permission.
    section_name = attr.ib(default=None, metadata={"tdx_name": "SectionName"})
