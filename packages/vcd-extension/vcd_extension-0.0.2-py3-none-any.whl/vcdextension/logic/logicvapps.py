"""
LogicVApps

:date: Jul 14, 2021
:author: Aldo Diaz, Marcelo Sureda

The LogicVApps class implements the logic to get the list of vApps and VMs in the organization.
It uses the services provided by the 'vcdextension' framework.
"""
from requests import status_codes

from vcdextension.entities.tenant import Tenant
from vcdextension.entities.virtualapp import VirtualApp
from vcdextension.libraries.exceptions import LogicExceptionHandler
from vcdextension.libraries.logger import Logger
from vcdextension.logic.logicvms import LogicVMs
from vcdextension.persistence.persistence import Persistence


class LogicVApps:
    """
    LogicVApps Class
    """
    _log = Logger()
    _config = Persistence().get_config()['vcd']

    @classmethod
    @LogicExceptionHandler
    def get_vapps_by_orgs(cls, tenant_id, context_id):
        """
        Implements the method get VApps list by organizations.

        :param str tenant_id: Org Id for which the report will be generated
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        tenant = Tenant(org_id=tenant_id, context_id=context_id)
        # Virtual DataCenters
        vdcs = tenant.get_virtual_datacenters(context_id=context_id)
        vapps_list = []
        for vdc in vdcs:
            # vApps in Virtual DataCenters
            vapps = vdc.get_vapps(context_id=context_id)
            for vapp in vapps:
                uri = 'https://' + cls._config['host'] + '/api/vApp/' + vapp.get_id()
                vapp_item = {'name': vapp.get_name(), 'id': vapp.get_id(), 'href': uri}
                vapps_list.append(vapp_item)
                # VMs in vApps
                vms = vapp.get_vms()
                for vm in vms:
                    uri = 'https://' + cls._config['host'] + '/api/vApp/' + vm.get_id()
                    vapp_item = {'name': vm.get_name(), 'id': vm.get_id(), 'href': uri}
                    vapps_list.append(vapp_item)
        return status_codes.codes.ok, {'response': 'ok', 'vApps': vapps_list}

    @classmethod
    @LogicExceptionHandler
    def get_methods_by_vapp(cls, context_id):
        """
        Implements the method get methods by vApp.

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        cls._log.info(f"Ctx={context_id}: Getting vApp methods")
        _, vm_methods = LogicVMs.get_methods_by_vm(context_id=context_id)
        vapp_methods = [x for x in dir(VirtualApp)
                        if callable(getattr(VirtualApp, x)) and not x.startswith('_')
                        and not x.startswith('get')]
        return status_codes.codes.ok, {'response': 'ok',
                                       'vapp_methods': vapp_methods,
                                       'vm_methods': vm_methods['vm_methods']}
