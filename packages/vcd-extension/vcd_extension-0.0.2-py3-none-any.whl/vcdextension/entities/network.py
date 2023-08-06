"""
Network

:date: Mar 21, 2021
:author: Aldo Diaz, Marcelo Sureda

Represents a simplified view of the Network element available in vCloud Director.
Allows framework's user to access network's settings and its allocated IPs.
"""

from abc import ABC
from pyvcloud.vcd.vdc_network import VdcNetwork
from requests import status_codes
from vcdextension.entities.entity import Entity, \
    VCDExtTypes
from vcdextension.libraries.constants import RightName
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments, \
    VCDExtensionNotImplemented, \
    VCDExtensionEntityNotFound
from vcdextension.libraries.vcloudsecurity import CheckPermissions


class NetworkBase(Entity, ABC):
    """
    Network Base class
    """

    def __init__(self, network_id=None, network_name=None, network_type=None, network_resource=None):
        """
        Network Base initializer

        :param str network_id: Network identifier
        :param str network_name: Network name
        :param VCDExtTypes network_type: Network type: VAPPNETWORK or NETWORK
        :param lxml.objectify.ObjectifiedElement network_resource: Network resource
        """
        super().__init__(entity_id=network_id, entity_name=network_name, entity_type=network_type)
        self._network_resource = network_resource

    def get_configuration(self):
        """
        Returns network settings

        :return: dict with network settings
        """
        network_config = {'name': self._name, 'id': self._id}
        # IsDeployed
        if hasattr(self._network_resource, 'IsDeployed'):
            network_config['deployed'] = bool(self._network_resource.IsDeployed)
        # Configuration
        if hasattr(self._network_resource, 'Configuration'):
            # FenceMode
            if hasattr(self._network_resource.Configuration, 'FenceMode'):
                network_config['mode'] = str(self._network_resource.Configuration.FenceMode)
            else:
                self._log.warning(f"No FenceMode attribute found for network '{self._name}'")
            # IpScopes
            if hasattr(self._network_resource.Configuration, 'IpScopes'):
                ip_scopes_list = []
                for ip_scope in self._network_resource.Configuration.IpScopes.IpScope:
                    ip_scope_item = {'gateway': str(ip_scope.Gateway),
                                     'netmask': str(ip_scope.Netmask)}
                    # IpRanges
                    if hasattr(ip_scope, 'IpRanges'):
                        ip_range_list = []
                        for ip_range in ip_scope.IpRanges.IpRange:
                            ip_range_item = {'start_address': str(ip_range.StartAddress),
                                             'end_address': str(ip_range.EndAddress)}
                            ip_range_list.append(ip_range_item)
                        ip_scope_item['ip_ranges'] = ip_range_list
                    ip_scopes_list.append(ip_scope_item)
                network_config['ip_scopes'] = ip_scopes_list
            else:
                self._log.warning(f"No IpScopes attribute found for network '{self._name}'")
        else:
            self._log.warning(f"No Configuration attribute found for network '{self._name}'")
        return network_config


class Network(NetworkBase):
    """
    Network elements in VirtualDataCenters
    """

    @CheckPermissions([RightName.ORGANIZATION_NETWORK_VIEW])
    def __init__(self, vdc=None, network_name=None, network_id=None, create=False, context_id=None):
        """
        VDC Network initializer

        :raises ValueError: Invalid argument received

        :param VirtualDataCenter vdc: VDC owning the Network
        :param str network_name: Network name
        :param str network_id: Network identifier
        :param bool create: True if new Network must be created inside vCloud
        :param str context_id: Context identifier
        """
        # Validate name argument
        if type(network_name) != str or network_name == "":
            message = f"Network not built. Invalid argument name '{network_name}'"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionInvalidArguments(message,
                                               status_code=status_codes.codes.bad_request,
                                               request_id=context_id)
        self.set_client()
        self._vdc = vdc
        # TODO Create new vCloud Network
        if create:
            message = f"Create new vCloud network '{network_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)
        # Access existing Network
        if network_name is None:
            # Get Network by id
            network_name, network_resource = self._get_name_and_resource(entity_id=network_id,
                                                                         entity_type=VCDExtTypes.NETWORK)
        else:
            # Get Network by VDC and name
            list_networks = self._vdc.get_pyvcloud_object() \
                .list_orgvdc_network_resources(name=network_name)
            if len(list_networks) > 0:
                network_resource = list_networks[0]
                network_id = network_resource.get('id').split(':')[-1]
                if network_id == "":
                    self._log.warning(f"Ctx={context_id}: Unable to get id from network '{network_name}' in "
                                      f"VDC '{self._vdc.get_name()}'. Using network name as id.")
                    network_id = network_name
            else:
                message = f"No network '{network_name}' found in VDC '{self._vdc.get_name()}': " \
                          "Network not built"
                self._log.error(f"Ctx={context_id}: " + message)
                raise VCDExtensionEntityNotFound(message,
                                                 status_code=status_codes.codes.not_found,
                                                 request_id=context_id)
        super().__init__(network_id=network_id, network_name=network_name,
                         network_type=VCDExtTypes.NETWORK, network_resource=network_resource)
        self._pyvcloud_object = VdcNetwork(self._client, resource=network_resource)
        self._log.info(f"Ctx={context_id}: Network object id '{network_id}', "
                       f"name '{network_name}' built successfully")

    def get_vdc(self):
        return self._vdc


class VappNetwork(NetworkBase):
    """
    Network elements in VApps
    """

    def __init__(self, vapp=None, network_name=None, create=False, context_id=None):
        """
        vApp Network initializer

        :raises ValueError: Invalid argument received

        :param Entity vapp: VApp owning the Network
        :param str network_name: Network name
        :param bool create: True if new Network must be created inside vCloud
        :param str context_id: Context identifier
        """
        # Validate name argument
        if type(network_name) != str or network_name == "":
            message = f"Network not built. Invalid argument name '{network_name}'"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionInvalidArguments(message,
                                               status_code=status_codes.codes.bad_request,
                                               request_id=context_id)
        self.set_client()
        self._vapp = vapp
        # TODO Create new vCloud vApp Network
        if create:
            message = f"Create new vCloud network '{network_name}': Not implemented"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNotImplemented(message,
                                             status_code=status_codes.codes.not_implemented,
                                             request_id=context_id)
        # Access existing Network
        vapp_resource = self._vapp.get_pyvcloud_object().get_resource()
        list_network_configs = vapp_resource.xpath(
            "//*[local-name()='NetworkConfigSection']/*[local-name()='NetworkConfig']")
        for network_config in list_network_configs:
            if network_config.get('networkName') == network_name and \
                    hasattr(network_config, 'Link'):
                network_id = network_config.Link.get('href').split('/network/')[1].split('/')[0]
                if network_id == "":
                    self._log.warning(f"Unable to get id for network '{network_name}' in "
                                      f"vApp '{self._vapp.get_name()}'. Using network name as id.")
                    network_id = network_name
                network_resource = network_config
                break
        else:
            message = f"No network '{network_name}' found in vApp '{self._vapp.get_name()}': " \
                      "Network not built"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityNotFound(message,
                                             status_code=status_codes.codes.not_found,
                                             request_id=context_id)
        super().__init__(network_id, network_name, VCDExtTypes.VAPPNETWORK, network_resource=network_resource)
        self._log.info(f"Ctx={context_id}: Network object id '{network_id}', name '{network_name}' "
                       f"in vApp '{self._vapp.get_name()}' built successfully")

    def get_vapp(self):
        return self._vapp
