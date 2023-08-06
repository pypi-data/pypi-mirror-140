import attr

from tdxapi.models.bases import TdxModel
from tdxapi.models.converters import to_datetime, to_uid
from tdxapi.models.custom_attribute_list import CustomAttributeList


@attr.s(kw_only=True)
class AssetSearch(TdxModel):
    __tdx_type__ = "TeamDynamix.Api.Assets.AssetSearch"

    #: The text to perform a LIKE search on the asset serial number and service tag.
    serial_like = attr.ib(default=None, metadata={"tdx_name": "SerialLike"})

    #: The search text to filter on. When specified, results will be sorted by their
    #: text relevancy.
    search_text = attr.ib(default=None, metadata={"tdx_name": "SearchText"})

    #: The ID of the saved search associated with this search.
    saved_search_id = attr.ib(default=None, metadata={"tdx_name": "SavedSearchID"})

    #: The current status IDs to filter on. Only assets that currently have one of
    #: these statuses will be included.
    status_ids = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "StatusIDs"})

    #: The external IDs to filter on. Only assets that have one of these external ID
    #: values will be included.
    external_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ExternalIDs"}
    )

    #: The "in service" status to filter on, based on the "out of service" flag for the
    #: status associated with the asset.
    is_in_service = attr.ib(default=None, metadata={"tdx_name": "IsInService"})

    #: The past status IDs to filter on. Only assets that have had one of these
    #: statuses will be included.
    status_ids_past = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "StatusIDsPast"}
    )

    #: The supplier IDs to filter on. Only assets that are supplied by one of these
    #: vendors will be included.
    supplier_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "SupplierIDs"}
    )

    #: The manufacturer IDs to filter on. Only assets that are manufactured by one of
    #: these vendors will be included.
    manufacturer_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ManufacturerIDs"}
    )

    #: The location IDs to filter on. Only assets that are associated with one of these
    #: locations will be included.
    location_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "LocationIDs"}
    )

    #: The location room ID to filter on. Only assets that are associated with this
    #: location room will be included.
    room_id = attr.ib(default=None, metadata={"tdx_name": "RoomID"})

    #: The parent asset IDs to filter on. Only assets that have one of these listed as
    #: a parent will be included.
    parent_ids = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "ParentIDs"})

    #: The contract IDs to filter on. Only assets that associated with one or more of
    #: these contracts will be included.
    contract_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ContractIDs"}
    )

    #: The contract IDs to exclude on. Only assets that are NOT associated with any of
    #: these contracts will be included.
    exclude_contract_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ExcludeContractIDs"}
    )

    #: The ticket IDs to filter on. Only assets that are associated with one or more of
    #: these tickets will be included.
    ticket_ids = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "TicketIDs"})

    #: The ticket IDs to exclude on. Only assets that are NOT associated with any of
    #: these tickets will be included.
    exclude_ticket_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ExcludeTicketIDs"}
    )

    #: The form IDs to filter on. Only assets that are associated with one or more of
    #: these forms will be included.
    form_ids = attr.ib(default=attr.Factory(list), metadata={"tdx_name": "FormIDs"})

    #: The product model IDs to filter on. Only assets that are associated with one of
    #: these product models will be included.
    product_model_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "ProductModelIDs"}
    )

    #: The maintenance window IDs to filter on. Only assets that are associated with
    #: one of these maintenance windows will be included.
    maintenance_schedule_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "MaintenanceScheduleIDs"}
    )

    #: The using account/department IDs to filter on. Only assets that are currently
    #: used by one or more of these accounts will be included.
    using_department_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "UsingDepartmentIDs"}
    )

    #: The requesting account/department IDs to filter on. Only assets that are listed
    #: as requested by one of these accounts will be included.
    requesting_department_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "RequestingDepartmentIDs"}
    )

    #: The owning account/department IDs to filter on. Only assets that are currently
    #: owned by one of these accounts will be included.
    owning_department_ids = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "OwningDepartmentIDs"}
    )

    #: The past owning account/department IDs to filter on. Only assets that have been
    #: historically owned by one or more of these accounts will be included.
    owning_department_ids_past = attr.ib(
        default=attr.Factory(list), metadata={"tdx_name": "OwningDepartmentIDsPast"}
    )

    #: The using person UIDs to filter on. Only assets that are currently used by one
    #: or more of these people will be included.
    using_customer_ids = attr.ib(
        default=attr.Factory(list),
        converter=to_uid,
        metadata={"tdx_name": "UsingCustomerIDs"},
    )

    #: The requestor UIDs to filter on. Only assets that are listed as requested by one
    #: of these people will be included.
    requesting_customer_ids = attr.ib(
        default=attr.Factory(list),
        converter=to_uid,
        metadata={"tdx_name": "RequestingCustomerIDs"},
    )

    #: The owner UIDs to filter on. Only assets that are currently owned by one of
    #: these people will be included.
    owning_customer_ids = attr.ib(
        default=attr.Factory(list),
        converter=to_uid,
        metadata={"tdx_name": "OwningCustomerIDs"},
    )

    #: The past owner UIDs to filter on. Only assets that have been historically owned
    #: by one or more of these people will be included.
    owning_customer_ids_past = attr.ib(
        default=attr.Factory(list),
        converter=to_uid,
        metadata={"tdx_name": "OwningCustomerIDsPast"},
    )

    #: The custom attributes to filter on.
    attributes = attr.ib(
        default=attr.Factory(CustomAttributeList),
        converter=CustomAttributeList.from_data,
        metadata={"tdx_name": "CustomAttributes"},
    )

    #: The minimum purchase cost to filter on.
    purchase_cost_from = attr.ib(
        default=None, metadata={"tdx_name": "PurchaseCostFrom"}
    )

    #: The maximum purchase cost to filter on.
    purchase_cost_to = attr.ib(default=None, metadata={"tdx_name": "PurchaseCostTo"})

    #: The contract provider ID to filter on. Only assets associated with at least one
    #: contract provided by this vendor will be included.
    contract_provider_id = attr.ib(
        default=None, metadata={"tdx_name": "ContractProviderID"}
    )

    #: The minimum acquisition date to filter on.
    acquisition_date_from = attr.ib(
        default=None,
        converter=to_datetime,
        metadata={"tdx_name": "AcquisitionDateFrom"},
    )

    #: The maximum acquisition date to filter on.
    acquisition_date_to = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "AcquisitionDateTo"}
    )

    #: The minimum expected replacement date to filter on.
    expected_replacement_date_from = attr.ib(
        default=None,
        converter=to_datetime,
        metadata={"tdx_name": "ExpectedReplacementDateFrom"},
    )

    #: The maximum expected replacement date to filter on.
    expected_replacement_date_to = attr.ib(
        default=None,
        converter=to_datetime,
        metadata={"tdx_name": "ExpectedReplacementDateTo"},
    )

    #: The minimum contract end date to filter on.
    contract_end_date_from = attr.ib(
        default=None,
        converter=to_datetime,
        metadata={"tdx_name": "ContractEndDateFrom"},
    )

    #: The maximum contract end date to filter on.
    contract_end_date_to = attr.ib(
        default=None, converter=to_datetime, metadata={"tdx_name": "ContractEndDateTo"}
    )

    #: Whether only parent assets should be returned.
    only_parent_assets = attr.ib(
        default=None, metadata={"tdx_name": "OnlyParentAssets"}
    )

    #: The maximum number of records to return.
    max_results = attr.ib(default=0, metadata={"tdx_name": "MaxResults"})
