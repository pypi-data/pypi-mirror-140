import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.custom_attribute_choice import CustomAttributeChoice


@attr.s(kw_only=True)
class CustomAttribute(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.CustomAttributes.CustomAttribute"

    #: The ID of the attribute.
    id = attr.ib(default=None, metadata={"tdx_name": "ID"})

    #: The ID of the attribute.
    name = attr.ib(default=None, metadata={"tdx_name": "Name"})

    #: The order of the attribute. Attributes are first sorted by order (ascending) and
    #: their name (also ascending).
    order = attr.ib(default=None, metadata={"tdx_name": "Order"})

    #: The description of the attribute.
    description = attr.ib(default=None, metadata={"tdx_name": "Description"})

    #: The ID of the section associated with the attribute.
    section_id = attr.ib(default=None, metadata={"tdx_name": "SectionID"})

    #: The name of the section associated with the attribute.
    section_name = attr.ib(default=None, metadata={"tdx_name": "SectionName"})

    #: The field type of the attribute.
    field_type = attr.ib(default=None, metadata={"tdx_name": "FieldType"})

    #: The data type of the attribute.
    data_type = attr.ib(default=None, metadata={"tdx_name": "DataType"})

    #: The choices associated with the attribute.
    choices = attr.ib(
        default=attr.Factory(list),
        converter=CustomAttributeChoice.from_data,
        metadata={"tdx_name": "Choices"},
    )

    #: The required status of the attribute.
    is_required = attr.ib(default=None, metadata={"tdx_name": "IsRequired"})

    #: The updatable status of the attribute.
    is_updatable = attr.ib(default=None, metadata={"tdx_name": "IsUpdatable"})

    #: The value of the attribute.
    value = attr.ib(default=None, metadata={"tdx_name": "Value"})

    #: The text value of the attribute. For choice attributes, this will be a
    #: comma-separated list of all the currently selected choices (referenced by choice
    #: ID).
    value_text = attr.ib(default=None, metadata={"tdx_name": "ValueText"})

    #: The text of the selected choices associated with the attribute. This will be a
    #: comma-separated list of the text of each selected choice.
    choices_text = attr.ib(default=None, metadata={"tdx_name": "ChoicesText"})

    #: The item types (represented as IDs) associated with the attribute.
    associated_item_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "AssociatedItemIDs"}
    )
