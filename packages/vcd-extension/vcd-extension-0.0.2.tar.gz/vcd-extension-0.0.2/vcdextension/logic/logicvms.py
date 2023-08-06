"""
LogicVMs

:date: Jul 14, 2021
:author: Aldo Diaz, Marcelo Sureda

The LogicVMs class implements the logic to get the list of VMs in the organization.
It uses the services provided by the 'vcdextension' framework.
"""
from requests import status_codes

from vcdextension.entities.tenant import Tenant
from vcdextension.entities.virtualmachine import VirtualMachine
from vcdextension.libraries.exceptions import LogicExceptionHandler
from vcdextension.libraries.logger import Logger
from vcdextension.persistence.persistence import Persistence


class LogicVMs:
    """
    LogicVMs Class
    """
    _log = Logger()
    _config = Persistence().get_config()['vcd']

    @classmethod
    @LogicExceptionHandler
    def get_vms_by_orgs(cls, tenant_id, context_id):
        """
        Implements the method get VMs by organizations.

        :param str tenant_id: Org Id for which the report will be generated
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        tenant = Tenant(org_id=tenant_id, context_id=context_id)
        # Virtual DataCenters
        vdcs = tenant.get_virtual_datacenters(context_id=context_id)
        vms_list = []
        for vdc in vdcs:
            # vApps in Virtual DataCenters
            vapps = vdc.get_vapps(context_id=context_id)
            for vapp in vapps:
                # VMs in vApps
                vms = vapp.get_vms()
                for vm in vms:
                    uri = 'https://' + cls._config['host'] + '/api/vApp/' + vm.get_id()
                    vm_item = {'name': vm.get_name(), 'id': vm.get_id(), 'href': uri}
                    vms_list.append(vm_item)
        return status_codes.codes.ok, {'response': 'ok', 'vms': vms_list}

    @classmethod
    @LogicExceptionHandler
    def get_methods_by_vm(cls, context_id):
        """
        Implements the method get methods by VM.

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        cls._log.info(f"Ctx={context_id}: Getting VM methods")
        vm_methods = [x for x in dir(VirtualMachine)
                      if callable(getattr(VirtualMachine, x)) and not x.startswith('_')
                      and not x.startswith('get')]
        return status_codes.codes.ok, {'response': 'ok',
                                       'vm_methods': vm_methods}
