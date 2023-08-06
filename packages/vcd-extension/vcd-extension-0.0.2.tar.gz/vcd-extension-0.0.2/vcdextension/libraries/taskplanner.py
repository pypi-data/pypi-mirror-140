"""
TaskPlanner

:date: Apr 28, 2021
:author: Aldo Diaz, Marcelo Sureda

Component that allows to group a set of executable tasks with an order of
precedence between them.
"""
from requests import status_codes
from vcdextension.entities.entity import VCDExtTypes
from vcdextension.entities.tenant import Tenant
from vcdextension.entities.virtualapp import VirtualApp
from vcdextension.entities.virtualdatacenter import VirtualDataCenter
from vcdextension.entities.virtualmachine import VirtualMachine
from vcdextension.entities.network import Network
from vcdextension.libraries.exceptions import VCDExtensionInvalidArguments
from vcdextension.libraries.logger import Logger
from vcdextension.libraries.vcloudsecurity import VCloudSecurity
from vcdextension.persistence.persistence import Persistence


class Task:
    """
    Task class
    Represents one single task inside a Plan
    """

    _log = Logger()
    _config = Persistence().get_config()['vcd']

    def __init__(self, entity_type, entity_id, action):
        """
        Initialize Task

        :param str entity_type:
        :param str entity_id:
        :param str action:
        """
        self._entity_type = entity_type.lower()
        self._entity_id = entity_id.lower()
        self._action = action.lower()

    def execute(self, tenant_id, context_id=None):
        """
        Execute task

        :param tenant_id: Tenant sent in URI
        :param context_id: Id of context
        :return:
        """

        if self._entity_type == VCDExtTypes.TENANT.value.lower():
            entity = Tenant(org_id=self._entity_id, context_id=context_id)
        elif self._entity_type == VCDExtTypes.VDC.value.lower():
            entity = VirtualDataCenter(vdc_id=self._entity_id, context_id=context_id)
        elif self._entity_type == VCDExtTypes.VAPP.value.lower():
            entity = VirtualApp(vapp_id=self._entity_id, context_id=context_id)
        elif self._entity_type == VCDExtTypes.VM.value.lower():
            entity = VirtualMachine(vm_id=self._entity_id, context_id=context_id)
        elif self._entity_type == VCDExtTypes.NETWORK.value.lower():
            entity = Network(network_id=self._entity_id, context_id=context_id)
        else:
            message = f"Invalid entity type {self._entity_type}"
            self._log.error(f"Ctx={context_id}: " + message)
            raise VCDExtensionInvalidArguments(message, request_id=context_id,
                                               status_code=status_codes.codes.bad_request)

        # Check if tenant of uri is the owner of the entity sent in task
        VCloudSecurity.entity_matches_tenant(entity, tenant_id, context_id)

        # Get function reference from action name
        if self._action is not None and self._action != "":
            function_reference = getattr(entity, self._action)
            # TODO Pass arguments to function (2)
            # return function_reference(*self._args, **self._kwargs)
            return function_reference(context_id=context_id)
        else:
            return None


class Plan:
    """
    Plan Class
    """
    _log = Logger()

    @classmethod
    def execute(cls, plan=None, tenant_id=None, context_id=None):
        """
        Execute plan

        :param plan: List of tasks
        :param tenant_id: Tenant sent in URI
        :param context_id: Id of context
        :return:
        """
        if plan is None:
            plan = []
        try:
            # Check if tenant in uri corresponds to tenant in security context
            VCloudSecurity().tenant_matches_context(tenant_id, context_id)
            for plan_item in plan:
                task = Task(plan_item['entity_type'], plan_item['entity_id'], plan_item['action'])
                # TODO Pass arguments to function (1)
                cls._log.info(f"Executing task: {plan_item}")
                task.execute(tenant_id, context_id=context_id)
        except Exception as e:
            cls._log.error(f"Ctx={context_id}: <<{type(e).__qualname__}>> {e}")
