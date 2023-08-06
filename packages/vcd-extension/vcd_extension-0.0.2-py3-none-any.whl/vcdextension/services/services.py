"""
Services

:date: Aug 1, 2021
:author: Aldo Diaz, Marcelo Sureda

The Services class receives the incoming request and calls the appropriate
methods from the logic component. After performing the corresponding
operations in the Logic class, formats and sends the response back.
"""
from vcdextension.logic.logicvapps import LogicVApps
from vcdextension.logic.logicorgs import LogicOrgs
from vcdextension.logic.logicvms import LogicVMs
from vcdextension.logic.logictasks import LogicTasks


class Services:
    """
    Services class
    """
    @staticmethod
    def svc_get_orgs(context_id):
        """
        Return organizations in the system

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicOrgs.get_orgs(context_id)

    @staticmethod
    def svc_methods_by_vapp(context_id):
        """
        Return methods of vApp and VM classes

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicVApps.get_methods_by_vapp(context_id)

    @staticmethod
    def svc_methods_by_vm(context_id):
        """
        Return methods of VM classes

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicVMs.get_methods_by_vm(context_id)

    @staticmethod
    def svc_vapps_by_organization(tenant_id, context_id):
        """
        Return vApps and VMs of the tenant

        :param str tenant_id: Tenant Id
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicVApps.get_vapps_by_orgs(tenant_id, context_id)

    @staticmethod
    def svc_vms_by_organization(tenant_id, context_id):
        """
        Return VMs of the tenant

        :param str tenant_id: Tenant Id
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicVMs.get_vms_by_orgs(tenant_id, context_id)

    @staticmethod
    def svc_get_scheduled_jobs(context_id):
        """
        Return scheduled jobs in the system

        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicTasks.get_scheduled_jobs(context_id)

    @staticmethod
    def svc_remove_job(context_id, job_id):
        """
        Return scheduled jobs in the system

        :param str context_id: Message context id
        :param str job_id: Scheduled Job identifier
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return LogicTasks.remove_job(context_id, job_id)
