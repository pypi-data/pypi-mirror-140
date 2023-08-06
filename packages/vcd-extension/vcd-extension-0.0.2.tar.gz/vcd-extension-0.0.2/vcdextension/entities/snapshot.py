"""
Snapshot

:date: Aug 10, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the Snapshot section available in VMs of vCloud Director.
Allows framework's user to access snapshots entities and operate on them.
"""
from dateutil import parser
from pyvcloud.vcd.client import NSMAP
from requests import status_codes

from vcdextension.entities.entity import Entity, VCDExtTypes
from vcdextension.libraries.constants import RightName
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, VCDExtensionEntityNotFound, \
    VCDExtensionAttributeNotAvailable
from vcdextension.libraries.vcloudsecurity import CheckPermissions


class Snapshot(Entity):
    """
    Snapshot Class
    Snapshot of a VM in vCloud Director.
    """

    @CheckPermissions([RightName.VAPP_SNAPSHOT_OPERATIONS])
    def __init__(self, vm=None, context_id=None):
        """
        Snapshot initializer

        :param vm: VM from which the snapshot is taken
        :param str context_id: Context identifier
        """
        if vm is None:
            message = "Snapshot not built. Required VM argument is None"
            self._log.error(message)
            raise VCDExtensionInvalidArguments(message,
                                               status_code=status_codes.codes.bad_request,
                                               request_id=context_id)
        self._vm = vm
        vm_resource = vm.get_pyvcloud_object().get_resource()
        snapshot_id = "snapshot-" + vm.get_id()
        snapshot_name = "snapshot-" + vm.get_name()

        snapshot_section = vm_resource.find('{' + NSMAP['ns10'] + '}SnapshotSection')
        snapshot = None
        if snapshot_section is not None:
            snapshot = snapshot_section.find('{' + NSMAP['ns10'] + '}Snapshot')
        if snapshot is not None:
            if 'created' in snapshot.keys():
                created_str = snapshot.get('created')
                self._creation_date = parser.parse(created_str)
                super().__init__(snapshot_id, snapshot_name, VCDExtTypes.SNAPSHOT)
                self._log.info(f"Ctx={context_id}: Snapshot id='{snapshot_id}', "
                               f"name='{snapshot_name}' built successfully")
        else:
            message = f"Snapshot not built." \
                      f"Snapshot not found for VirtualMachine id={vm.get_id()}"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id)

    def get_vm(self):
        """
        Return VM from which the snapshot was taken

        :return: VM entity
        """
        return self._vm

    def get_creation_date(self, context_id=None):
        """
        Return creation date of the snapshot

        :return: datetime: Snapshot creation date
        """
        if hasattr(self, '_creation_date'):
            return self._creation_date
        else:
            message = f"Attribute 'creation_date' doesn't exist in Snapshot id='{self._id}'"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionAttributeNotAvailable(message,
                                                    status_code=status_codes.codes.internal_server_error,
                                                    request_id=context_id)

    @CheckPermissions([RightName.VAPP_SNAPSHOT_OPERATIONS])
    def remove(self, context_id=None):
        """
        Removes snapshot
        """
        try:
            self._vm.get_pyvcloud_object().snapshot_remove_all()
        except Exception as e:
            self._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> Snapshot id='{self.get_id()}'"
                            f" remove error {e}")
            raise e
