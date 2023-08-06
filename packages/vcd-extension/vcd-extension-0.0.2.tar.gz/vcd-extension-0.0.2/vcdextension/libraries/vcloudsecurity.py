"""
vCloud Security

:date: Mar 12, 2021
:author: Aldo Diaz, Marcelo Sureda

VCloud Director Security module is responsible for authentication, and
permissions validations.
"""
from enum import Enum
from pyvcloud.vcd.client import BasicLoginCredentials, \
    Client, \
    find_link, \
    NSMAP, \
    RelationType
from pyvcloud.vcd.exceptions import VcdException
from pyvcloud.vcd.org import Org
from requests import status_codes
from requests.packages.urllib3 import disable_warnings
from vcdextension.entities.entity import VCDExtTypes
from vcdextension.libraries import constants
from vcdextension.libraries.exceptions import VCDExtensionSecurity, \
    VCDExtensionAuthenticationError, \
    VCDExtensionConnectionError, VCDExtensionEntityDoesNotBelongToTenant, VCDExtensionInvalidArguments, \
    VCDExtensionNonExistentUser, VCDExtensionAttributeNotAvailable
from vcdextension.libraries.logger import Logger
from vcdextension.persistence.persistence import Persistence


class CommonRoles(Enum):
    CATALOG_AUTHOR = 'Catalog Author'
    CONSOLE_ACCESS_ONLY = 'Console Access Only'
    ORGANIZATION_ADMINISTRATOR = 'Organization Administrator'
    VAPP_AUTHOR = 'vApp Author'
    VAPP_USER = 'vApp User'


class VCloudSecurity:
    """
    VCloudSecurity Class
    VCloud Director Security module is responsible for authentication, and
    permissions validations. Implementation of the Singleton pattern.
    """

    _instance = None
    _log = Logger()
    _persistence = Persistence()
    _config = None

    def __new__(cls):
        # Get configuration
        cls._config = cls._persistence.get_config()['vcd']
        if cls._instance is None:
            cls._instance = super(VCloudSecurity, cls).__new__(cls)
            cls._instance.__client = cls.__login()
        return cls._instance

    @classmethod
    def __login(cls):
        """
        Authenticate with vCloud Director server

        :raise VCDExtensionConnectionError: Connection to vCD server fails
        :raise VCDExtensionAuthenticationError: Authentication with vCD server fails

        :return class Client: Low-level interface object to vCloud REST API
        """
        if not cls._config['verify'] and cls._config['disable_ssl_warnings']:
            disable_warnings()

        # Perform vCloud Director server authentication
        try:
            client = Client(cls._config['host'],
                            api_version=cls._config['api_version'],
                            verify_ssl_certs=cls._config['verify'],
                            log_file=constants.LOG_DIR + '/' + constants.PYVCLOUD_LOG_FILE,
                            log_requests=True,
                            log_headers=True,
                            log_bodies=True)
            client.set_credentials(BasicLoginCredentials(cls._config['user'],
                                                         cls._config['org'],
                                                         cls._config['password']))
        except ConnectionError:
            message = f"VCD host {cls._config['host']}: connection error"
            cls._log.error(message)
            raise VCDExtensionConnectionError(message,
                                              status_code=status_codes.codes.bad_gateway,
                                              request_id='N/A') from ConnectionError
        except VcdException:
            message = f"VCD host {cls._config['host']}: authentication error"
            cls._log.error(message)
            raise VCDExtensionAuthenticationError(message,
                                                  status_code=status_codes.codes.unauthorized,
                                                  request_id='N/A') from VcdException

        cls._log.info(f"VCD host {cls._config['host']}: successful authentication")
        return client

    @classmethod
    def logout(cls):
        """
        Logout from the vCloud Director server
        """
        try:
            cls._instance.__client.logout()
            cls._log.info(f"VCD host {cls._config['host']} logged out")
        except Exception as e:
            cls._log.error(f"<<{type(e).__qualname__}>> {e}")

    def get_client(self):
        """
        Get client to the vCloud Director REST API

        :return: ApiClient
        """
        return self._instance.__client

    def add_context(self, ctx_id, ctx_msg):
        """
        Save new context message to contexts dictionary

        :param ctx_id: Message id
        :param ctx_msg: Message context
        """
        self._persistence.save(ctx_id, ctx_msg)

    def get_context(self, context_id):
        """
        Get context message from contexts dictionary

        :param context_id: Context id of message
        :return str user_id: User sending request
                str org_id: Org id of user
                str user_org_name: Org name of user
                list rights: Associated permissions
        """
        context = self._persistence.load(context_id)
        if context is False:
            message = f"Context not found"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionSecurity(message,
                                       status_code=status_codes.codes.forbidden,
                                       request_id=context_id)
        # Get Organization ID of user sending request
        permissions = context[1]
        user_id = permissions['user'].split(':')[-1]
        org_id = permissions['org'].split(':')[-1]
        uri = 'https://' + self._config['host'] + '/api/org/' + org_id
        org_resource = self.__client.get_resource(uri)
        org_name = org_resource.get('name')
        rights = permissions['rights']
        return user_id, org_id, org_name, rights

    def del_context(self, ctx_id):
        """
        Delete context message from contexts dictionary

        :param ctx_id: Message id
        """
        # Check if context must be kept
        context = self._persistence.load(ctx_id)
        if context is False:
            return
        if 'keep_context' in context[0] and context[0]['keep_context'] is True:
            return
        self._persistence.remove(ctx_id)
        self._persistence.save_db_file()

    def keep_context(self, ctx_id, keep=False):
        """
        Save new context message to contexts dictionary

        :param ctx_id: Message id
        :param Bool keep: Indicates if context must be kept
        """
        # Check if context exists
        context = self._persistence.load(ctx_id)
        if context is False:
            self._log.error(f"Context id '{ctx_id}' not found")
            return
        context[0]['keep_context'] = keep
        self._persistence.save(ctx_id, context)
        if keep:
            self._persistence.save_db_file()

    def get_orgs(self, context_id=None):
        """
        Organizations list

        :param str context_id: Id of context
        :return: dict of org names and hrefs
        """
        _, org_id, org_name, _ = self.get_context(context_id)
        if org_name.lower() == "system":
            org_resources = self.__client.get_org_list()
            org_list = []
            for org_resource in org_resources:
                name = org_resource.get('name')
                href = org_resource.get('href')
                identifier = href.split('/')[-1]
                org_item = {'name': name, 'id': identifier, 'href': href}
                org_list.append(org_item)
        else:
            uri = 'https://' + self._config['host'] + '/api/org/' + org_id
            org_resource = self.__client.get_resource(uri)
            name = org_resource.get('name')
            href = org_resource.get('href')
            org_list = [{'name': name, 'id': org_id, 'href': href}]
        return org_list

    @classmethod
    def get_corresponding_tenant(cls, entity, context_id):
        """
        Returns the ID and pyvcloud object of the tenant that owns the entity

        :param Entity entity: vcdExtension entity
        :param str context_id: Id of context
        :raises VCDExtensionSecurity: If entity is not found in the iteration
        :return: str org_id: Organization id
                 Org pyvcloud_tenant: Org pyvcloud object with tenant that owns the entity
        """
        # Verify entity type
        if entity.get_type() == VCDExtTypes.TENANT:
            return entity.get_id(), entity.get_pyvcloud_object()

        if entity.get_type() == VCDExtTypes.SNAPSHOT:
            entity = entity.get_vm()
        elif entity.get_type() == VCDExtTypes.VAPPNETWORK:
            entity = entity.get_vapp()
        elif entity.get_type() == VCDExtTypes.NETWORK:
            entity = entity.get_vdc()

        try:
            # Start iteration from the current entity: VM, VAPP or VDC
            entity_type_list = [VCDExtTypes.VM, VCDExtTypes.VAPP, VCDExtTypes.VDC, VCDExtTypes.TENANT]
            entity_type_list = entity_type_list[entity_type_list.index(entity.get_type())+1:]
            pyvcloud_object = entity.get_pyvcloud_object()
            resource = pyvcloud_object.get_resource()
            # Iterate all the way UP from the current entity to the owning tenant
            for entity_type in entity_type_list:
                entity_link = find_link(resource, RelationType.UP,
                                        f'application/vnd.vmware.vcloud.{entity_type.value}+xml')
                resource = cls._instance.__client.get_resource(entity_link.href)
            org_id = resource.get('href').split('/')[-1]
            return org_id, Org(cls._instance.__client, resource=resource)
        except Exception as e:
            message = f"<<{type(e).__qualname__}>> {e}"
            cls._log.error(message)
            raise VCDExtensionSecurity(message,
                                       status_code=status_codes.codes.not_found,
                                       request_id=context_id) from e

    @classmethod
    def tenant_matches_context(cls, tenant_id, context_id):
        """
        Checks if the tenant passed corresponds to the tenant
        of the user in the context_id

        :param str tenant_id: Tenant Id
        :param str context_id: Message context identifier
        :raises VCDExtensionEntityDoesNotBelongToTenant
        :return str org_id: Tenant identifier
        """
        # Get user and organization from context
        user, user_org_id, user_org_name, _ = cls._instance.get_context(context_id)

        # Check if they match with Id of tenant passed in the URI
        if user_org_name.lower() != "system" and user_org_id != tenant_id:
            message = f"User '{user}' from org '{user_org_name}' doesn't belong to tenant '{tenant_id}'"
            cls._log.error(message)
            raise VCDExtensionEntityDoesNotBelongToTenant(message,
                                                          status_code=status_codes.codes.forbidden,
                                                          request_id=context_id)
        else:
            return tenant_id

    @classmethod
    def entity_matches_tenant(cls, entity, tenant_id, context_id):
        """
        Check if tenant is the owner of the entity

        :param Entity entity: entity
        :param str tenant_id: Tenant identifier
        :param str context_id: Message context identifier
        :raises: VCDExtensionEntityDoesNotBelongToTenant
        :return str owner_name: Name of tenant
        """
        owner_id, pyvcloud_owner = cls.get_corresponding_tenant(entity, context_id)
        owner_name = pyvcloud_owner.get_name()
        if owner_name.lower() != "system" and tenant_id != owner_id:
            message = f"Entity {entity.get_type()} with id '{entity.get_id()}' does not belong to tenant "\
                      f"'{owner_name}'"
            cls._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionEntityDoesNotBelongToTenant(message, request_id=context_id,
                                                          status_code=status_codes.codes.bad_request)
        return owner_name

    @classmethod
    def get_user(cls, user_id, context_id):
        uri = 'https://' + cls._config['host'] + '/api/admin/user/' + user_id
        user_resource = cls._instance.__client.get_resource(uri)
        if user_resource is None:
            message = f"User id {user_id} not found"
            cls._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionNonExistentUser(message, request_id=context_id,
                                              status_code=status_codes.codes.unauthorized)
        else:
            return user_resource


class CheckPermissions:
    """
    CheckPermissions class is used as decorator to validate
    entity access by the user sending the request.
    """
    _log = Logger()

    def __init__(self, rights=None):
        if rights is None:
            rights = []
        self._rights = rights

    def __call__(self, function):
        def check_permissions_wrapper(*args, **kwargs):
            """
            Check permissions in decorated functions

            :param args: decorated function positional arguments
            :param kwargs: decorated function keyword arguments
            :return: function result
            """
            # Get request context with user id & permissions
            if 'context_id' in kwargs:
                context_id = kwargs['context_id']
                vcd_security = VCloudSecurity()
                user, user_org_id, user_org_name, user_rights = vcd_security.get_context(context_id)
            else:
                message = "Security context not present"
                self._log.error(f"Ctx=None: " + message)
                raise VCDExtensionSecurity(message,
                                           status_code=status_codes.codes.forbidden,
                                           request_id='not present')

            # Function invocation if calling an __init__() method
            result = None
            if function.__name__ == '__init__':
                result = function(*args, **kwargs)

            # Get Tenant from entity arguments. This is done after __init__() function
            # invocation in order to access the Entity object once is fully initialized.
            # args[0] corresponds to the the first (self) argument in all class methods.
            org_id, pyvcd_org = VCloudSecurity.get_corresponding_tenant(args[0], context_id)

            # Check if the user sending the request belongs to the same
            # organization of the accessed entity
            if user_org_name.lower() != "system" and user_org_id != org_id:
                message = f"User '{user}' doesn't belong to tenant '{org_id}'"
                self._log.error(message)
                raise VCDExtensionEntityDoesNotBelongToTenant(message,
                                                              status_code=status_codes.codes.forbidden,
                                                              request_id=context_id)

            # Check required permissions are present in the request context
            for right in self._rights:
                right_record = pyvcd_org.get_right_record(right.value)
                right_id = right_record['href'].split('/admin/right/')[-1]
                right_urn = "urn:vcloud:right:" + right_id
                if right_urn not in user_rights:
                    message = f"User '{user}' with no permission '{right.value}'"
                    self._log.error(message)
                    raise VCDExtensionSecurity(message,
                                               status_code=status_codes.codes.forbidden,
                                               request_id=context_id)
            # Function invocation for non __init__() methods
            if function.__name__ != '__init__':
                result = function(*args, **kwargs)
            return result

        return check_permissions_wrapper


class CheckUserAccess:
    """
    CheckUserAccess class is used as decorator to validate
    the user in the request context has access to the vApp.
    """
    _log = Logger()

    def __call__(self, function):
        def check_user_access_wrapper(*args, **kwargs):
            """
            Check user access to vApp in decorated functions

            :param args: decorated function positional arguments
            :param kwargs: decorated function keyword arguments
            :return: function result
            """
            # Get request context with user id & permissions
            if 'context_id' in kwargs:
                context_id = kwargs['context_id']
                vcd_security = VCloudSecurity()
                user_id, user_org_id, user_org_name, user_rights = vcd_security.get_context(context_id)
            else:
                message = "Security context not present"
                self._log.error(message)
                raise VCDExtensionSecurity(message,
                                           status_code=status_codes.codes.forbidden,
                                           request_id='not present')

            result = function(*args, **kwargs)
            # Verify if entity is a vApp
            entity_type = args[0].get_type()
            if entity_type == VCDExtTypes.VAPP:
                vapp = args[0]
            else:
                message = f"Invalid entity type {entity_type}"
                self._log.error(message)
                raise VCDExtensionInvalidArguments(message, status_code=status_codes.codes.not_found,
                                                   request_id=context_id)

            # Verify if user is system administrator
            if user_org_name.lower() != "system":
                user = VCloudSecurity.get_user(user_id, context_id)
                role_tree = user.find('{' + NSMAP['ns10'] + '}Role')
                if role_tree is None:
                    message = f"Role section not found for user id {user_id}"
                    self._log.error(message)
                    raise VCDExtensionAttributeNotAvailable(message, status_code=status_codes.codes.not_found,
                                                            request_id=context_id)
                role = str(role_tree.get('name'))
                # Verify if user is organization administrator
                if role != CommonRoles.ORGANIZATION_ADMINISTRATOR.value:
                    vapp_acl = vapp.get_pyvcloud_object().get_access_settings()
                    if vapp_acl is None:
                        message = f"Access Control List not found in vApp {vapp.get_name()}"
                        self._log.error(message)
                        raise VCDExtensionInvalidArguments(message, status_code=status_codes.codes.not_found,
                                                           request_id=context_id)
                    # Verify if the vApp is shared to everyone
                    is_shared = bool(vapp_acl.find('{' + NSMAP['ns10'] + '}IsSharedToEveryone'))
                    if not is_shared:
                        # Verify if the user has access to the vApp
                        access_list = vapp_acl.xpath(
                            "//*[local-name()='AccessSettings']/*[local-name()='AccessSetting']")
                        user_name = user.get('name')

                        for access_setting in access_list:
                            access_subject = access_setting.find('{' + NSMAP['ns10'] + '}Subject')
                            access_user_name = str(access_subject.get('name'))
                            if access_user_name == user_name:
                                break
                        else:
                            message = f"User {user_name} with no access to vApp {vapp.get_name()}"
                            self._log.error(message)
                            raise VCDExtensionSecurity(message, status_code=status_codes.codes.forbidden,
                                                       request_id=context_id)
            return result

        return check_user_access_wrapper
