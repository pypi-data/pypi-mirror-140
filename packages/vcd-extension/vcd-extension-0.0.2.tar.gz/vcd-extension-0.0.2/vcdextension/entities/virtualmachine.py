"""
VirtualMachine

:date: Mar 21, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the VM element available in vCloud Director.
Allows framework's user to access the resources associated to the VM and to
execute actions on it.
"""

from pyvcloud.vcd.exceptions import OperationNotSupportedException
from pyvcloud.vcd.client import find_link, RelationType, VCLOUD_STATUS_MAP
from pyvcloud.vcd.vm import VM
from requests import status_codes
from vcdextension.entities.entity import Entity, \
    VCDExtTypes
from vcdextension.entities.snapshot import Snapshot
from vcdextension.libraries.constants import RightName
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, \
    VCDExtensionNotImplemented, \
    VCDExtensionEntityNotFound
from vcdextension.libraries.vcloudsecurity import CheckPermissions


class VirtualMachine(Entity):
    """
    VirtualMachine element inside VirtualApp
    """

    def __init__(self, vapp=None, vm_name=None, vm_id=None, create=False, context_id=None):
        """
        VirtualMachine initializer

        :raises VCDExtensionInvalidArguments: Invalid argument received
        :raises VCDExtensionEntityNotFound: VM not found

        :param VirtualApp vapp: VApp owning the VM
        :param str vm_name: VM name
        :param bool create: True if new VM must be created inside vCloud
        :param str context_id: Context identifier
        """
        self._vapp = vapp
        # Validate name argument
        if vm_id is None:
            if type(vm_name) != str or vm_name == "":
                message = f"VM not built. Invalid argument name '{vm_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)
            elif vapp is None:
                message = f"VM not built. VirtualApp is required to build VM '{vm_name}'"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionInvalidArguments(message,
                                                   status_code=status_codes.codes.bad_request,
                                                   request_id=context_id)

        self.set_client()
        # TODO Create new VM
        if create:
            message = f"Create new vCloud VM '{vm_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)

        # Access existing VM
        try:
            if vm_name is None:
                # Get VM by id
                vm_name, vm_resource = self._get_name_and_resource(vm_id, VCDExtTypes.VM)
            else:
                # Get VM by name and vApp to which belongs
                pyvcd_vapp = vapp.get_pyvcloud_object()
                vm_resource = pyvcd_vapp.get_vm(vm_name)
                vm_id = vm_resource.get('href').split('/')[-1]
            super().__init__(vm_id, vm_name, VCDExtTypes.VM)
            self._pyvcloud_object = VM(self._client, resource=vm_resource)
        except Exception as e:
            vapp_name = "None" if vapp is None else vapp.get_name()
            message = f"VM id '{vm_id}', name '{vm_name}' " \
                      f"not found in vApp '{vapp_name}': VM not built"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id) from e
        self._log.info(f"Ctx={context_id}: VirtualMachine object id '{vm_id}', "
                       f"name '{vm_name}' built successfully")

    def get_vapp(self, context_id=None):
        """
        Returns the vApp owning the VM

        :return: VirtualApp
        """
        from vcdextension.entities.virtualapp import VirtualApp
        if self._vapp is None:
            resource = self._pyvcloud_object.get_resource()
            link_vapp = find_link(resource, RelationType.UP, 'application/vnd.vmware.vcloud.vApp+xml')
            vapp_id = link_vapp.href.split('/api/vApp/')[-1]
            self._vapp = VirtualApp(vapp_id=vapp_id, context_id=context_id)
        return self._vapp

    def get_resources(self):
        """
        Returns VM resources: CPUs, memory, disks.

        :return: dict with VM resources
        """
        vm_config = {'name': self._name, 'id': self._id}
        try:
            resources = self._pyvcloud_object.get_cpus()
            resources['memory'] = self._pyvcloud_object.get_memory()
        except Exception as e:
            self._log.error(f"Error getting CPU and Memory resources for VM '{self._name}': {e}")
            resources = {}

        disks = []
        vm_resource = self._pyvcloud_object.get_resource()
        if hasattr(vm_resource.VmSpecSection, 'DiskSection'):
            if hasattr(vm_resource.VmSpecSection.DiskSection,
                       'DiskSettings'):
                for disk_setting in \
                        vm_resource.VmSpecSection.DiskSection.DiskSettings:
                    disk = {'disk_id': int(disk_setting.DiskId),
                            'size': int(disk_setting.SizeMb)}
                    if hasattr(disk_setting, 'StorageProfile'):
                        disk['name'] = disk_setting.StorageProfile.get('name')
                    disks.append(disk)
        else:
            self._log.warning(f"No DiskSection attribute found for VM '{self._name}'")
        resources['disks'] = disks
        vm_config['resources'] = resources
        return vm_config

    @CheckPermissions([RightName.VAPP_EDIT_VM_CPU, RightName.VAPP_EDIT_VM_MEMORY])
    def set_resources(self, new_resources, context_id=None):
        """
        Set VM CPU and/or memory

        :param dict new_resources: New values for CPU (keys 'num_cpus' and 'num_cores_per_socket')
            and/or memory (key 'memory')
        :param str context_id: Context identifier
        :return: None
        """
        self._pyvcloud_object.reload()
        original_state = self._pyvcloud_object.get_power_state()
        # VM should be in state Powered off = 8
        if original_state != 8:
            self.power_off(context_id=context_id)

        # Update CPU if present in new_resources
        if 'num_cpus' in new_resources:
            num_cpus = new_resources['num_cpus']
            num_cores_per_socket = None if 'num_cores_per_socket' in new_resources else \
                new_resources['num_cores_per_socket']
            try:
                result = self._pyvcloud_object.modify_cpu(num_cpus, num_cores_per_socket)
                task = self._client.get_task_monitor().wait_for_status(
                    task=result,
                    timeout=60,
                    poll_frequency=2,
                    callback=None)
                self._log.info(f"Ctx={context_id}: VirtualMachine id='{self._id}' "
                               f"update CPU status {task.get('status')}")
            except Exception as e:
                self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> "
                                f"VirtualMachine id='{self._id}' update CPU error {e}")

        # Update memory if present in new_resources
        if 'memory' in new_resources:
            try:
                result = self._pyvcloud_object.modify_memory(new_resources['memory'])
                task = self._client.get_task_monitor().wait_for_status(
                    task=result,
                    timeout=60,
                    poll_frequency=2,
                    callback=None)
                self._log.info(f"Ctx={context_id}: VirtualMachine id='{self._id}' "
                               f"modify memory status {task.get('status')}")
            except Exception as e:
                self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> "
                                f"VirtualMachine id='{self._id}' modify memory error {e}")

        # Return to original state if it was Powered on = 4
        if original_state == 4:
            self.power_on(context_id=context_id)

    @CheckPermissions([RightName.VAPP_VIEW_VM_METRICS])
    def get_current_metrics(self, context_id=None):
        """
        Returns VM current metrics. If the VM is powered off then
        it's powered on, current metrics taken, and powered off again.

        :param str context_id: Context identifier
        :return: list current metrics
        """
        try:
            self._pyvcloud_object.reload()
            original_state = self._pyvcloud_object.get_power_state()
            # VM should be in state Powered on = 4
            if original_state != 4:
                self.power_on(context_id=context_id)
            metrics = self._pyvcloud_object.list_all_current_metrics()
            # Return to original state if it was Powered off = 8
            if original_state == 8:
                self.power_off(context_id=context_id)
        except OperationNotSupportedException as e:
            self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> Current metrics not "
                            f"available for VirtualMachine id='{self._id}' {e}")
            metrics = []
        return metrics

    @CheckPermissions([RightName.VAPP_VIEW_VM_METRICS])
    def get_historic_metrics(self, context_id=None):
        """
        Returns VM metrics

        :param str context_id: Context identifier
        :return: list historic metrics
        """
        try:
            metrics = self._pyvcloud_object.list_all_historic_metrics()
        except OperationNotSupportedException as e:
            self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>>: Historic metrics not "
                            f"available for VirtualMachine id='{self._id}' {e}")
            metrics = []
        return metrics

    @CheckPermissions([RightName.VAPP_POWER_OPERATIONS])
    def power_off(self, context_id=None):
        """
        Powers off the VirtualMachine

        :param str context_id: Context identifier
        """
        try:
            result = self._pyvcloud_object.power_off()
            task = self._client.get_task_monitor().wait_for_status(
                task=result,
                timeout=60,
                poll_frequency=2,
                callback=None)
            self._log.info(f"Ctx={context_id}: VirtualMachine '{self._id}' power off result {task.get('status')}")
            self._pyvcloud_object.reload()
            self._log.info(f"Ctx={context_id}: Current VirtualMachine '{self._id}' state "
                           f"{VCLOUD_STATUS_MAP.get(int(self._pyvcloud_object.get_power_state()))}")
        except Exception as e:
            self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> "
                            f"VirtualMachine id='{self._id}' power off error {e}")

    @CheckPermissions([RightName.VAPP_POWER_OPERATIONS])
    def power_on(self, context_id=None):
        """
        Powers on the VirtualMachine
        """
        try:
            result = self._pyvcloud_object.power_on()
            task = self._client.get_task_monitor().wait_for_status(
                task=result,
                timeout=60,
                poll_frequency=2,
                callback=None)
            self._log.info(f"Ctx={context_id}: VirtualMachine id '{self._id}' power on result {task.get('status')}")
            self._pyvcloud_object.reload()
            self._log.info(f"Ctx={context_id}: Current VirtualMachine '{self._id}' state "
                           f"{VCLOUD_STATUS_MAP.get(int(self._pyvcloud_object.get_power_state()))}")
        except Exception as e:
            self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> "
                            f"VirtualMachine id='{self._id}' power on error {e}")

    def get_snapshot(self, context_id=None):
        """
        Returns the VM snapshot

        :param str context_id: Context identifier
        :return: Snapshot of VM
        """
        self.set_client()
        self._pyvcloud_object.reload()
        try:
            snapshot = Snapshot(self, context_id=context_id)
            return snapshot
        except VCDExtensionEntityNotFound:
            return None
