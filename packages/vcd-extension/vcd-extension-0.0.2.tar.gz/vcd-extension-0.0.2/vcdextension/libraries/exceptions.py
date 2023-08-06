"""
Exceptions

:date: Apr 15, 2021
:author: Aldo Diaz, Marcelo Sureda

Exceptions created during vcd Extension processing.
"""
from requests import status_codes
from vcdextension.libraries.logger import Logger


class VCDExtensionBase(Exception):
    """
    Base class for all vCloud Director Extension exceptions.
    """
    def __init__(self, *args, status_code, request_id=None):
        """
        Initialize base VCD Extension Exception class

        :param args: arg[0] is the exception message
        :param int status_code: status code in the response
        :param str request_id: message request id
        """
        if args:
            self.message = args[0]
        else:
            self.message = None
        self.status_code = status_code
        self.request_id = request_id

    def __str__(self):
        return f"Status code {self.status_code} [Request id: {self.request_id}] {self.message if self.message else ''}"


class VCDExtensionConnectionError(VCDExtensionBase):
    """
    Raised when VCD server connection fails
    """
    def __str__(self):
        return "VCD Connection Error: " +\
               super(VCDExtensionConnectionError, self).__str__()


class VCDExtensionAuthenticationError(VCDExtensionBase):
    """
    Raised when VCD authentication fails
    """
    def __str__(self):
        return "VCD Authentication error: " +\
               super(VCDExtensionAuthenticationError, self).__str__()


class VCDExtensionSecurity(VCDExtensionBase):
    """
    Raised when vCD security validation fails
    """
    def __str__(self):
        return "Security Exception: " +\
               super(VCDExtensionSecurity, self).__str__()


class VCDExtensionInvalidArguments(VCDExtensionBase):
    """
    Raised when argument validation fails
    """
    def __str__(self):
        return "Invalid Arguments Exception: " +\
               super(VCDExtensionInvalidArguments, self).__str__()


class VCDExtensionEntityNotFound(VCDExtensionBase):
    """
    Raised when a VCD entity is not found
    """
    def __str__(self):
        return "Entity Not Found Exception: " +\
               super(VCDExtensionEntityNotFound, self).__str__()


class VCDExtensionEntityDoesNotBelongToTenant(VCDExtensionBase):
    """
    Raised when a VCD entity doesn't belong to Tenant
    """
    def __str__(self):
        return "Entity Not Found Exception: " +\
               super(VCDExtensionEntityDoesNotBelongToTenant, self).__str__()


class VCDExtensionNotImplemented(VCDExtensionBase):
    """
    Raised when calling not implemented function
    """
    def __str__(self):
        return "Not Implemented (yet) Exception: " +\
               super(VCDExtensionNotImplemented, self).__str__()


class VCDExtensionAttributeNotAvailable(VCDExtensionBase):
    """
    Raised when trying to access not available attribute
    """
    def __str__(self):
        return "Attribute Not Available Exception: " +\
               super(VCDExtensionAttributeNotAvailable, self).__str__()


class VCDExtensionNonExistentUser(VCDExtensionBase):
    """
    Raised when user doesn't exist
    """
    def __str__(self):
        return "User doesn't exists: " +\
               super(VCDExtensionNonExistentUser, self).__str__()


class LogicExceptionHandler:
    """
    LogicExceptionHandler class is used as decorator to handle
    in the logic layer those exceptions raised in lower layers.
    """
    _log = Logger()

    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        """
        Handle and catch exceptions received at logic layer

        :param args: decorated function positional arguments
        :param kwargs: decorated function keyword arguments
        :return: function result
        """
        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            else:
                status_code = status_codes.codes.server_error
            self._log.error(f"<<{type(e).__qualname__}>> {e}")
            return status_code, {'response': str(e)}
