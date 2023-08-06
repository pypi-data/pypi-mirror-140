"""
Entity

:date: Mar 11, 2021
:author: Aldo Diaz, Marcelo Sureda

The Entities component models a generic entity present in vCloud Director
used to fulfill required operations.
"""

from enum import Enum

from vcdextension.libraries.logger import Logger
from vcdextension.persistence.persistence import Persistence


class VCDExtTypes(Enum):
    TENANT = "org"
    VDC = "vdc"
    VAPP = "vApp"
    VM = "vm"
    NETWORK = "network"
    VAPPNETWORK = "vapp-network"
    SNAPSHOT = "snapshot"


class Entity:
    """
    Entity Class
    Generic representation of a vCloud Director entity.
    """
    _log = Logger()
    _config = Persistence().get_config()['vcd']
    _client = None

    def __init__(self, entity_id, entity_name, entity_type):
        """
        Entity initializer

        :param str entity_id: Entity identifier
        :param str entity_name: Entity name
        :param VCDExtTypes entity_type: Entity type
        """
        self._id = entity_id
        self._name = entity_name
        self._type = entity_type
        self._pyvcloud_object = None

    def get_id(self):
        """
        Return entity identifier
        :return: str id
        """
        return self._id

    def get_name(self):
        """
        Return entity name
        :return: str name
        """
        return self._name

    def get_type(self):
        """
        Return entity type
        :return: VCDExtTypes
        """
        return self._type

    def get_pyvcloud_object(self):
        """
        Return the Org Pyvcloud object
        :return: pyvcloud object
        """
        return self._pyvcloud_object

    @classmethod
    def set_client(cls):
        """
        Update class attribute _client
        """
        from vcdextension.libraries.vcloudsecurity import VCloudSecurity
        vcd_security = VCloudSecurity()
        cls._client = vcd_security.get_client()

    @classmethod
    def _get_name_and_resource(cls, entity_id, entity_type):
        """
        Find the name and resource from the entity id and type
        :param str entity_id: Entity identifier
        :param VCDExtTypes entity_type: Entity type
        :return: str entity name,
                 lxml.objectify.ObjectifiedElement resource
        """
        uri_type = VCDExtTypes.VAPP.value if entity_type == VCDExtTypes.VM else entity_type.value
        uri = 'https://' + cls._config['host'] + '/api/' + uri_type + '/' + entity_id
        cls.set_client()
        resource = cls._client.get_resource(uri)
        name = resource.get('name')
        return name, resource
