"""
VirtualApp

:date: Mar 17, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the VApp element available in vCloud Director.
Allows framework's user to access associated virtual machines and networks.
"""

from pyvcloud.vcd.client import NSMAP, find_link, RelationType, VCLOUD_STATUS_MAP
from pyvcloud.vcd.vapp import VApp
from requests import status_codes
from vcdextension.entities.entity import Entity, \
    VCDExtTypes
from vcdextension.entities.network import VappNetwork
from vcdextension.entities.virtualmachine import VirtualMachine
from vcdextension.libraries.constants import RightName
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, \
    VCDExtensionNotImplemented, \
    VCDExtensionEntityNotFound
from vcdextension.libraries.vcloudsecurity import CheckPermissions, CheckUserAccess


class VirtualApp(Entity):
    """
    VirtualApp element inside VirtualDataCenter
    """

    @CheckUserAccess()
    def __init__(self, vdc=None, vapp_name=None, vapp_id=None, create=False, context_id=None):
        """
        VirtualApp initializer

        :raises VCDExtensionInvalidArguments: Invalid argument received
        :raises VCDExtensionEntityNotFound: VirtualApp not found

        :param VirtualDataCenter vdc: Virtual Data Center owning the VApp
        :param str vapp_name: VApp name
        :param str vapp_id: VApp identifier
        :param bool create: True if new VApp must be created inside vCloud
        :param str context_id: Context identifier
        """
        self._vdc = vdc
        # Validate arguments
        if vapp_id is None:
            if type(vapp_name) != str or vapp_name == "":
                message = f"vApp not built. Invalid argument name '{vapp_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)
            elif vdc is None:
                message = f"vApp not built. Virtual Data Center is required to build vApp '{vapp_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)

        self.set_client()
        # TODO Create new VApp
        if create:
            message = f"Create new vCloud vApp '{vapp_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)

        try:
            if vapp_name is None:
                # Get vApp by id
                vapp_name, vapp_resource = self._get_name_and_resource(vapp_id, VCDExtTypes.VAPP)
            else:
                # Get vApp by name and VDC to which belongs
                pyvcd_vdc = vdc.get_pyvcloud_object()
                vapp_resource = pyvcd_vdc.get_vapp(vapp_name)
                vapp_id = vapp_resource.get('href').split('/')[-1]
            super().__init__(vapp_id, vapp_name, VCDExtTypes.VAPP)
            self._pyvcloud_object = VApp(self._client, resource=vapp_resource)
        except Exception as e:
            vdc_name = "None" if vdc is None else vdc.get_name()
            message = f"vApp with id='{vapp_id}', name='{vapp_name}' in VDC '{vdc_name}' " \
                      "not found: vApp not built"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id) from e
        self._log.info(f"Ctx={context_id}: VirtualApp object id '{vapp_id}', name='{vapp_name}' built successfully")

    def get_vms(self, context_id=None):
        """
        Returns VMs in this VApp

        :param str context_id: Context identifier
        :return: list of VMs
        """
        self.set_client()
        results = []
        for vm_item in self._pyvcloud_object.get_all_vms():
            vm = VirtualMachine(self, vm_item.get('name'), context_id=context_id)
            results.append(vm)
        return results

    def get_networks(self, context_id=None):
        """
        Returns all networks in this vApp

        :param str context_id: Context identifier
        :return: list of Network objects
        """
        self.set_client()
        results = []
        all_networks = self._pyvcloud_object.get_all_networks()
        for network_item in all_networks:
            network_name = network_item.get('{' + NSMAP['ovf'] + '}name')
            if network_name != 'none':
                network = VappNetwork(vapp=self, network_name=network_name, context_id=context_id)
                results.append(network)
        return results

    def get_vdc(self, context_id=None):
        """
        Returns Virtual Data Center to which this vApp belongs to.

        :return: VirtualDataCenter
        """
        from vcdextension.entities.virtualdatacenter import VirtualDataCenter
        if self._vdc is None:
            resource = self._pyvcloud_object.get_resource()
            link_vdc = find_link(resource, RelationType.UP, 'application/vnd.vmware.vcloud.vdc+xml')
            vdc_id = link_vdc.href.split('/api/vdc/')[-1]
            self._vdc = VirtualDataCenter(vdc_id=vdc_id, context_id=context_id)
        return self._vdc

    @CheckPermissions([RightName.VAPP_POWER_OPERATIONS])
    def power_off(self, context_id=None):
        """
        Powers off the VirtualApp
        """
        try:
            result = self._pyvcloud_object.power_off()
            task = self._client.get_task_monitor().wait_for_status(
                task=result,
                timeout=60,
                poll_frequency=2,
                callback=None)
            self._log.info(f"Ctx={context_id}: vApp='{self._id}' power off result {task.get('status')}")
            self._pyvcloud_object.reload()
            self._log.info(f"Ctx={context_id}: Current vApp='{self._id}' "
                           f"state {VCLOUD_STATUS_MAP.get(int(self._pyvcloud_object.get_power_state()))}")
        except Exception as e:
            self._log.error(f"Ctx={context_id}: vApp id='{self._id}' power off error "
                            f"<<{type(e).__qualname__}>> {e}")

    @CheckPermissions([RightName.VAPP_POWER_OPERATIONS])
    def power_on(self, context_id=None):
        """
        Powers on the VirtualApp
        """
        try:
            result = self._pyvcloud_object.power_on()
            task = self._client.get_task_monitor().wait_for_status(
                task=result,
                timeout=60,
                poll_frequency=2,
                callback=None)
            self._log.info(f"vApp {self._id} power on result {task.get('status')}")
            self._pyvcloud_object.reload()
            self._log.info(f"Current vApp '{self._id}' "
                           f"state {VCLOUD_STATUS_MAP.get(int(self._pyvcloud_object.get_power_state()))}")
        except Exception as e:
            self._log.error(f"Ctx={context_id}: vApp id='{self._id}' power on error "
                            f"<<{type(e).__qualname__}>> {e}")
