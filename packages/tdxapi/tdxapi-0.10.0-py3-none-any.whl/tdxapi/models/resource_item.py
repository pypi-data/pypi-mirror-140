import attr

from tdxapi.models.bases import TdxModel


@attr.s(kw_only=True)
class ResourceItem(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.ResourceItem"

    #: The role the resource has on the associated item.
    role = attr.ib(default=None, metadata={"tdx_name": "ItemRole"})

    #: The name of the resource.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The initials to be displayed if no profile image is specified for the resource.
    initials = attr.ib(default=None, metadata={"tdx_name": "Initials"})

    #: The value of the resource.
    id = attr.ib(default=None, metadata={"tdx_name": "Value"})

    #: The integer ID of the resource.
    ref_id = attr.ib(default=None, metadata={"tdx_name": "RefValue"})

    #: The profile image file name of the resource.
    profile_image_file_name = attr.ib(
        default=None, metadata={"tdx_name": "ProfileImageFileName"}
    )
