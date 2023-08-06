"""
Tenant

:date: Mar 11, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the Org element available in vCloud Director.
It's an entry point that allows the user to navigate to the virtual Data
Centers that the Tenant has available.
"""

from pyvcloud.vcd.org import Org
from requests import status_codes
from vcdextension.entities.entity import Entity
from vcdextension.entities.entity import VCDExtTypes
from vcdextension.entities.virtualdatacenter import VirtualDataCenter
from vcdextension.libraries.constants import RightName
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, \
    VCDExtensionNotImplemented, \
    VCDExtensionEntityNotFound
from vcdextension.libraries.vcloudsecurity import CheckPermissions


class Tenant(Entity):
    """
    Tenant Class
    Org entity of vCloud Director.
    """

    @CheckPermissions([RightName.ORGANIZATION_VIEW])
    def __init__(self, org_id=None, org_name=None, create=False, context_id=None):
        """
        Tenant initializer. Validates arguments

        :raises VCDExtensionInvalidArguments: Invalid arguments received
        :raises VCDExtensionEntityNotFound: Tenant not found
        :raises VCDExtensionSecurity: Not authorized access

        :param str org_id: Organization identifier
        :param str org_name: Organization name
        :param bool create: True if new Org must be created inside vCloud
        :param str context_id: Context identifier
        """
        # Validate arguments
        if (type(org_id) != str or org_id == "") and \
                (type(org_name) != str or org_name == ""):
            message = f"Tenant object not built. Invalid arguments id '{org_id}', name '{org_name}'"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionInvalidArguments(message,
                                               status_code=status_codes.codes.bad_request,
                                               request_id=context_id)

        self.set_client()
        # TODO Create new Organization
        if create:
            message = f"Create new vCloud Tenant '{org_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)

        try:
            if org_name is None:
                # Get Organization by id
                org_name, org_resource = self._get_name_and_resource(org_id, VCDExtTypes.TENANT)
            else:
                # Get Organization by name
                org_id, org_resource = self.get_org_id_and_resource(org_name)
            super().__init__(org_id, org_name, VCDExtTypes.TENANT)
            self._pyvcloud_object = Org(self._client, resource=org_resource)
        except Exception as e:
            message = f"Tenant with id '{org_id}', name '{org_name}' not found: tenant not built"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id) from e
        self._log.info(f"Ctx={context_id}: Tenant object id '{org_id}', name '{org_name}' built successfully")

    @classmethod
    def get_org_id_and_resource(cls, org_name):
        """

        :param org_name:
        :return:
        """
        cls.set_client()
        org_resource = cls._client.get_org_by_name(org_name)
        org_id = org_resource.get('href').split('/')[-1]
        return org_id, org_resource

    def get_virtual_datacenters(self, context_id=None):
        """
        List all VDCs that are backing the current organization.

        :param str context_id: Context identifier

        :return: List of VDCs in the organization.
        """
        self.set_client()
        results = []
        for vdc_item in self._pyvcloud_object.list_vdcs():
            vdc = VirtualDataCenter(tenant=self, vdc_name=vdc_item['name'], context_id=context_id)
            results.append(vdc)
        return results
