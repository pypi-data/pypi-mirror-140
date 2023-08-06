"""
ServiceRabbitMQ

:date: Apr 1, 2021
:author: Aldo Diaz, Marcelo Sureda

The ServiceRabbitMQ class exposes the services to the frontend and implements
the services component instantiating the abstract class RabbitMQClient.
Isolates the Service class from the RabbitMQ specifics.
"""
from requests import status_codes
from vcdextension.libraries.logger import Logger
from vcdextension.persistence.persistence import Persistence
from vcdextension.libraries.rabbitmqclient import RabbitMQClient
from vcdextension.services.services import Services


class CheckValidMethod:
    """
    CheckValidMethods class is used as decorator to validate
    allowed HTTP methods (GET, PUT, POST, DELETE) in each endpoint.
    """
    _log = Logger()

    def __init__(self, allowed_methods=None):
        """
        Init CheckValidMethod class

        :param allowed_methods: list of HTTP methods allowed in the function
        """
        if allowed_methods is None:
            allowed_methods = []
        self._allowed_methods = [x.upper() for x in allowed_methods]

    def __call__(self, function):
        def check_method_wrapper(*args, **kwargs):
            """
            Check valid HTTP method in decorated functions

            :param args: decorated function positional arguments
            :param kwargs: decorated function keyword arguments
            :return: function result
            """
            if 'method' not in kwargs:
                self._log.error(f"Request id={kwargs['context_id'] if 'context_id' in kwargs else 'Not Available'} "
                                f"method argument not received in {function.__name__}")
                return status_codes.codes.method_not_allowed, {'response': 'Method Not Allowed'}
            method = kwargs['method']
            if method.upper() in self._allowed_methods:
                return function(*args, **kwargs)
            else:
                self._log.error(f"Request id={kwargs['context_id'] if 'context_id' in kwargs else 'Not Available'} "
                                f"invalid method {method} received for function {function.__name__}")
                return status_codes.codes.method_not_allowed, {'response': 'Method Not Allowed'}

        return check_method_wrapper


class ServiceRabbitMQ(RabbitMQClient):
    """
    RabbitMQClient abstract class implementation
    Log object inherited from RabbitMQClient
    """
    def process_request(self, request):
        """
        Process the request and executes the backend operations.

        :param dict request: request message
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        uri = request['requestUri']

        # Get configuration
        p = Persistence()
        config = p.get_config()['extension']

        # Validate URL
        if not uri.startswith(config['prefix']):
            message = f"Request id={request['id']} malformed URL endpoint {uri}"
            self._log.error(message)
            return status_codes.codes.not_found, {'response': message}

        # Parse URL
        endpoint = uri[len(config['prefix']):]
        uri_parameters = endpoint.split('/')
        uri_parameters = [x for x in uri_parameters if x != ""]
        if len(uri_parameters) == 1:
            if uri_parameters[0] == "orgs":
                # Organizations list: /orgs
                return self._request_get_orgs(method=request['method'], context_id=request['id'])
            elif uri_parameters[0] == "jobs":
                # Jobs list: /jobs
                return self._request_get_scheduled_jobs(method=request['method'], context_id=request['id'])
        elif len(uri_parameters) == 2:
            if uri_parameters[0] == "vapp":
                if uri_parameters[1] == "methods":
                    # List vApps and VMs methods or tasks: /vapp/methods
                    return self._request_methods_by_vapp(method=request['method'], context_id=request['id'])
            elif uri_parameters[0] == "vm":
                if uri_parameters[1] == "methods":
                    # List VMs methods or tasks: /vm/methods
                    return self._request_methods_by_vm(method=request['method'], context_id=request['id'])
            elif uri_parameters[0] == "job":
                job_id = uri_parameters[1]
                # Remove job id: /job/{job_id}
                return self._request_remove_job(method=request['method'], context_id=request['id'], job_id=job_id)
        elif len(uri_parameters) == 3:
            if uri_parameters[0] == "org":
                tenant_id = uri_parameters[1]
                if uri_parameters[2] == "vapps":
                    # List of VApps and VMs by organization: /org/{id}/vapps
                    return self._request_vapps_by_organization(method=request['method'], tenant_id=tenant_id,
                                                               context_id=request['id'])
                if uri_parameters[2] == "vms":
                    # List of VMs by organization: /org/{id}/vms
                    return self._request_vms_by_organization(method=request['method'], tenant_id=tenant_id,
                                                             context_id=request['id'])

        # Redirect control to customer use cases
        return self.process_customer_requests(uri_parameters=uri_parameters, method=request['method'],
                                              body=request['body'], context_id=request['id'])

    def process_customer_requests(self, uri_parameters=None, method=None, body=None, context_id=None):
        """
        Process the customer request. A customized use case
        is implemented overriding this method.

        :param list uri_parameters: Parameters received in the URI
        :param str method: HTTP request method
        :param dict body: Message request body
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        # If we got here something went wrong
        self._log.error(f"Ctx={context_id}: Malformed URL or operation not implemented")
        return status_codes.codes.not_implemented, {'response': 'Not implemented'}

    @CheckValidMethod(["GET"])
    def _request_get_orgs(self, method=None, context_id=None):
        """
        Processes the request message to get orgs in the system.

        :param str method: HTTP request method
        :param str context_id: Message context id
        :return: int resp_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_get_orgs(context_id)

    @CheckValidMethod(["GET"])
    def _request_methods_by_vapp(self, method=None, context_id=None):
        """
        Processes the request message to get methods of vApps and VMs.

        :param str method: HTTP request method
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_methods_by_vapp(context_id)

    @CheckValidMethod(["GET"])
    def _request_methods_by_vm(self, method=None, context_id=None):
        """
        Processes the request message to get methods of VMs.

        :param str method: HTTP request method
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_methods_by_vm(context_id)

    @CheckValidMethod(["GET"])
    def _request_vapps_by_organization(self, method=None, tenant_id=None, context_id=None):
        """
        Processes the request message to get vapps and vms by organization.

        :param str method: HTTP request method
        :param str tenant_id: Tenant Id
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_vapps_by_organization(tenant_id, context_id)

    @CheckValidMethod(["GET"])
    def _request_vms_by_organization(self, method=None, tenant_id=None, context_id=None):
        """
        Processes the request message to get vms by organization.

        :param str method: HTTP request method
        :param str tenant_id: Tenant Id
        :param str context_id: Message context id
        :return: int status_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_vms_by_organization(tenant_id, context_id)

    @CheckValidMethod(["GET"])
    def _request_get_scheduled_jobs(self, method=None, context_id=None):
        """
        Processes the request message to get scheduled jobs in the system.

        :param str method: HTTP request method
        :param str context_id: Message context id
        :return: int resp_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_get_scheduled_jobs(context_id)

    @CheckValidMethod(["DELETE"])
    def _request_remove_job(self, method=None, context_id=None, job_id=None):
        """
        Processes the request message to remove a job in the system.

        :param str method: HTTP request method
        :param str context_id: Message context id
        :param str job_id: Scheduled Job identifier
        :return: int resp_code: Status code to respond to frontend,
                 dict resp_body: Body with response or error detail
        """
        return Services.svc_remove_job(context_id, job_id)
