from tdxapi.dispatcher import Dispatcher
from tdxapi.managers.account import AccountManager
from tdxapi.managers.application import ApplicationManager
from tdxapi.managers.asset_app import AssetApplication
from tdxapi.managers.attachment import AttachmentManager
from tdxapi.managers.custom_attribute import CustomAttributeManager
from tdxapi.managers.custom_attribute_choice import CustomAttributeChoiceManager
from tdxapi.managers.functional_role import FunctionalRoleManager
from tdxapi.managers.group import GroupManager
from tdxapi.managers.location import LocationManager
from tdxapi.managers.location_room import LocationRoomManager
from tdxapi.managers.report import ReportManager
from tdxapi.managers.resource_pool import ResourcePoolManager
from tdxapi.managers.security_role import SecurityRoleManager
from tdxapi.managers.ticket_app import TicketApplication


class TdxClient(object):
    def __init__(self, organization, beid=None, wskey=None, use_sandbox=False):
        self.dispatcher = Dispatcher(
            organization, beid=beid, wskey=wskey, use_sandbox=use_sandbox
        )

        self.applications = ApplicationManager(self.dispatcher)
        self.accounts = AccountManager(self.dispatcher)
        self.attachments = AttachmentManager(self.dispatcher)
        self.attributes = CustomAttributeManager(self.dispatcher)
        self.attribute_choices = CustomAttributeChoiceManager(self.dispatcher)
        self.functional_roles = FunctionalRoleManager(self.dispatcher)
        self.groups = GroupManager(self.dispatcher)
        self.locations = LocationManager(self.dispatcher)
        self.resource_pools = ResourcePoolManager(self.dispatcher)
        self.reports = ReportManager(self.dispatcher)
        self.rooms = LocationRoomManager(self.dispatcher)
        self.security_roles = SecurityRoleManager(self.dispatcher)

        self.apps = {}

        for a in self.applications.all():
            if a.app_class == "TDAssets":
                self.apps[a.id] = AssetApplication(self.dispatcher, a.id)
            elif a.app_class == "TDTickets":
                self.apps[a.id] = TicketApplication(self.dispatcher, a.id)

    def asset_app(self, app_id: int) -> AssetApplication:
        return self.apps[app_id]

    def ticket_app(self, app_id: int) -> TicketApplication:
        return self.apps[app_id]
