"""
LogicTasks

:date: Dec 15, 2021
:author: Aldo Diaz, Marcelo Sureda

The LogicTasks class implements the logic to get the list of scheduled jobs in the system.
It uses the services provided by the 'vcdextension' framework.
"""
from requests import status_codes

from vcdextension.libraries.exceptions import LogicExceptionHandler
from vcdextension.libraries.taskscheduler import TaskScheduler


class LogicTasks:
    """
    LogicTasks Class
    """

    @classmethod
    @LogicExceptionHandler
    def get_scheduled_jobs(cls, context_id):
        """
        Implements the method get scheduled jobs.

        :param context_id: Message context id
        :return: dict with response status and list of scheduled jobs.
        """
        scheduler = TaskScheduler()
        job_list = scheduler.list_jobs(context_id)
        return status_codes.codes.ok, {'response': 'ok', 'jobs': job_list}

    @classmethod
    @LogicExceptionHandler
    def remove_job(cls, context_id, job_id):
        """
        Implements the method remove jobs.

        :param context_id: Message context id
        :param str job_id: Scheduled Job identifier
        :return: dict with response status.
        """
        scheduler = TaskScheduler()
        scheduler.remove_job(context_id, job_id)
        return status_codes.codes.ok, {'response': 'ok'}
