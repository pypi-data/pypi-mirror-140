from enum import IntEnum


class UserType(IntEnum):
    """Types of users and customers tracked within TeamDynamix."""

    __tdx_type__ = "TeamDynamix.Api.Users.UserType"

    #: Indicates that the type of the user could not be determined. Should not be used
    #: in normal operations.
    NONE = 0

    #: Indicates that the user is classified as a full TeamDynamix user.
    USER = 1

    #: Indicates that the user is classified as a customer, which means that they cannot
    #: log in to TeamDynamix.
    CUSTOMER = 2

    #: Indicates that the user is classified as a resource placeholder. These users act
    #: as a placeholder for actual users when planning out projects without knowing
    #: exactly who will be acting as the resource in question.
    RESOURCE_PLACEHOLDER = 8

    #: Indicates that the user is classified as a service account. These users will be
    #: able to authenticate and use the API, but they will not be able to log in to
    #: TDNext, TDMobile, TDAdmin, or TDClient.
    SERVICE_ACCOUNT = 9
