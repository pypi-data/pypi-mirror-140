import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid


@attr.s(kw_only=True)
class ConfigurationItemRelationship(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Cmdb.ConfigurationItemRelationship"

    #: The ID of the relationship.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the parent configuration item associated with the relationship.
    parent_id = attr.ib(default=None, metadata={"tdx_name": "ParentID"})

    #: The name of the parent configuration item associated with the relationship.
    parent_name = attr.ib(default=None, metadata={"tdx_name": "ParentName"})

    #: The ID of the type associated with the relationship's parent configuration item.
    parent_type_id = attr.ib(default=None, metadata={"tdx_name": "ParentTypeID"})

    #: The name of the type associated with the relationship's parent configuration
    #: item.
    parent_type_name = attr.ib(default=None, metadata={"tdx_name": "ParentTypeName"})

    #: The ID of the child configuration item associated with the relationship.
    child_id = attr.ib(default=None, metadata={"tdx_name": "ChildID"})

    #: The name of the child configuration item associated with the relationship.
    child_name = attr.ib(default=None, metadata={"tdx_name": "ChildName"})

    #: The ID of the type associated with the relationship's child configuration item.
    child_type_id = attr.ib(default=None, metadata={"tdx_name": "ChildTypeID"})

    #: The name of the type associated with the relationship's child configuration
    #: item.
    child_type_name = attr.ib(default=None, metadata={"tdx_name": "ChildTypeName"})

    #: Whether this relationship is maintained automatically by the system.
    is_system_defined = attr.ib(
        default=None, metadata={"tdx_name": "IsSystemMaintained"}
    )

    #: The ID of the type associated with the relationship.
    relationship_type_id = attr.ib(
        default=None, metadata={"tdx_name": "RelationshipTypeID"}
    )

    #: The description of the relationship from the perspective of the parent
    #: configuration item.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The description of the relationship from the perspective of the child
    #: configuration item.
    inverse_description = attr.ib(
        default=None, metadata={"tdx_name": "InverseDescription"}
    )

    #: Whether the relationship is an operational dependency.
    is_operational_dependency = attr.ib(
        default=None, metadata={"tdx_name": "IsOperationalDependency"}
    )

    #: The created date of the relationship.
    created_date = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "CreatedDateUtc"}
    )

    #: The UID of the user who created the relationship.
    created_uid = attr.ib(
        default=None, converter=to_uid, metadata={"tdx_name": "CreatedUID"}
    )

    #: The full name of the user who created the relationship.
    created_full_name = attr.ib(default=None, metadata={"tdx_name": "CreatedFullName"})
