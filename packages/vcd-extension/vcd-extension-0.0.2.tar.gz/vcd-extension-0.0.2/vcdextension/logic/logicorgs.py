"""
LogicOrgs

:date: Jun 23, 2021
:author: Aldo Diaz, Marcelo Sureda

The LogicOrgs class implements the logic to get the list of organizations in the system.
It uses the services provided by the 'vcdextension' framework.
"""
from requests import status_codes

from vcdextension.libraries.exceptions import LogicExceptionHandler
from vcdextension.libraries.logger import Logger
from vcdextension.libraries.vcloudsecurity import VCloudSecurity


class LogicOrgs:
    """
    LogicOrgs Class
    """
    _log = Logger()

    @classmethod
    @LogicExceptionHandler
    def get_orgs(cls, context_id):
        """
        Implements the method get organizations list.

        :param context_id: Message context id
        :return: dict with response status and list of organizations.
        """
        vcd_security = VCloudSecurity()
        orgs_list = vcd_security.get_orgs(context_id)
        return status_codes.codes.ok, {'response': 'ok', 'orgs': orgs_list}
