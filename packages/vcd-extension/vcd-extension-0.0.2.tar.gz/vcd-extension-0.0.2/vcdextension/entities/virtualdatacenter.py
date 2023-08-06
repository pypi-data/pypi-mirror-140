"""
VirtualDataCenter

:date: Mar 14, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the VDC element available in vCloud Director.
It belongs to an organization. Allows the user to access the vApps and VMs of
this VirtualDataCenter.
"""

from pyvcloud.vcd.client import EntityType, \
    find_link, \
    RelationType
from pyvcloud.vcd.vdc import VDC
from requests import status_codes
from vcdextension.libraries.constants import RightName
from vcdextension.entities.entity import Entity, \
    VCDExtTypes
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, \
    VCDExtensionNotImplemented, \
    VCDExtensionEntityNotFound, VCDExtensionSecurity
from vcdextension.entities.virtualapp import VirtualApp
from vcdextension.entities.network import Network
from vcdextension.libraries.vcloudsecurity import CheckPermissions


class VirtualDataCenter(Entity):
    """
    VirtualDataCenter Class
    VDC entity of vCloud Director.
    """

    @CheckPermissions([RightName.ORGANIZATION_VDC_VIEW])
    def __init__(self, tenant=None, vdc_name=None, vdc_id=None, create=False, context_id=None):
        """
        VirtualDataCenter initializer.

        :raises VCDExtensionInvalidArguments: Invalid arguments received
        :raises VCDExtensionEntityNotFound: VirtualDataCenter not found
        :raises VCDExtensionSecurity: Not authorized access

        :param Tenant tenant: VirtualDataCenter identifier
        :param str vdc_name: VirtualDataCenter name
        :param bool create: True if new VDC must be created inside vCloud
        :param str context_id: Context identifier
        """
        self._tenant = tenant
        # Validate arguments
        if vdc_id is None:
            if type(vdc_name) != str or vdc_name == "":
                message = f"VDC not built. Invalid argument name '{vdc_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)
            elif tenant is None:
                message = f"VDC not built. Tenant is required to build VDC '{vdc_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)

        self.set_client()
        # TODO Create new VDC
        if create:
            message = f"Create new vCloud VDC '{vdc_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)

        # Access existing VDC
        try:
            if vdc_name is None:
                # Get VDC by id
                vdc_name, vdc_resource = self._get_name_and_resource(vdc_id, VCDExtTypes.VDC)
            else:
                # Get VDC by name and tenant to which belongs
                pyvcd_org = tenant.get_pyvcloud_object()
                vdc_resource = pyvcd_org.get_vdc(vdc_name)
                vdc_id = vdc_resource.get('href').split('/')[-1]
            super().__init__(vdc_id, vdc_name, VCDExtTypes.VDC)
            self._pyvcloud_object = VDC(self._client, resource=vdc_resource)
        except Exception as e:
            tenant_name = "None" if tenant is None else tenant.get_name()
            message = f"VDC with id '{vdc_id}', name '{vdc_name}' in Tenant '{tenant_name}' not found: " \
                      "VDC not built"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id) from e
        self._log.info(f"Ctx={context_id}: VDC object id '{vdc_id}', name '{vdc_name}' built successfully")

    def get_vapps(self, context_id=None):
        """
        Returns all vApps in this Virtual Data Center.

        :param str context_id: Context identifier

        :return: list of vApps
        """
        self.set_client()
        results = []
        for vapp_item in self._pyvcloud_object.list_resources(entity_type=EntityType.VAPP):
            try:
                vapp = VirtualApp(vdc=self, vapp_name=vapp_item['name'], context_id=context_id)
                results.append(vapp)
            except VCDExtensionSecurity:
                self._log.info(f"Ctx={context_id}: vApp '{vapp_item['name']}' not accessible")
        return results

    def get_networks(self, context_id=None):
        """
        Returns all networks that belong to the Data Center.

        :param str context_id: Context identifier

        :return: list of Networks
        """
        results = []
        for network_item in self._pyvcloud_object.list_orgvdc_network_records():
            network = Network(vdc=self, network_name=network_item['name'], context_id=context_id)
            results.append(network)
        return results

    def get_tenant(self, context_id=None):
        """
        Return the Tenant owner of the VDC

        :return: Tenant object
        """
        from vcdextension.entities.tenant import Tenant
        if self._tenant is None:
            resource = self._pyvcloud_object.get_resource()
            link_tenant = find_link(resource, RelationType.UP, 'application/vnd.vmware.vcloud.org+xml')
            org_id = link_tenant.href.split('/api/org/')[-1]
            self._tenant = Tenant(org_id=org_id, context_id=context_id)
        return self._tenant
