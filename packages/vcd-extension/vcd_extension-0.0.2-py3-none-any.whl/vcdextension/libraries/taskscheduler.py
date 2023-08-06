"""
TaskScheduler

:date: Apr 28, 2021
:author: Aldo Diaz, Marcelo Sureda

Provides the functionality of scheduling programmable activities. It's the
main system _scheduler. Allows to execute repeatable tasks daily, weekly or
monthly.
"""
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from vcdextension.libraries.logger import Logger
from vcdextension.libraries.vcloudsecurity import VCloudSecurity


class TaskScheduler:
    """
    TaskScheduler class
    Provides scheduling functionality. It's a Pythonic
    implementation of the singleton pattern.
    """
    _instance = None
    _log = Logger()

    def __new__(cls):
        if cls._instance is None:
            # Initializes the scheduler
            try:
                cls._instance = super(TaskScheduler, cls).__new__(cls)
                cls._instance._scheduler = BackgroundScheduler(jobstores={'default': RedisJobStore()},
                                                               executors={'default': ThreadPoolExecutor(10)},
                                                               job_defaults={'coalesce': True, 'max_instances': 1})
                cls._instance._scheduler.start()
                cls._log.info("Task scheduler successfully started")
            except Exception as e:
                cls._log.error(f"<<{type(e).__qualname__}>> {e}")
                del cls._instance
                return None
        return cls._instance

    def schedule_job(self, func, kwargs, **trigger_args):
        """
        Adds the given job to the task scheduler.

        :param Any func: Function to be scheduled
        :param dict kwargs: Keyword arguments
        :param Any trigger_args: Trigger arguments to define execution times
        :return: str: Job reference
        """
        context_id = None
        # If present, the context should be saved for future reference
        if 'context_id' in kwargs:
            context_id = kwargs['context_id']
            vcd_security = VCloudSecurity()
            vcd_security.keep_context(context_id, True)

        # Generate Job ID: Concatenate function name to context ID and hash it
        job_id = str(abs(hash(func.__name__ + str(kwargs))))

        self._scheduler.add_job(func, trigger='cron', args=[], kwargs=kwargs, id=job_id, jobstore='default',
                                executor='default', replace_existing=True, **trigger_args)
        self._log.info(f"Ctx={context_id}: Scheduled job id '{job_id}' with chron params={trigger_args}")
        return job_id

    def remove_job(self, context_id, job_id):
        """
        Removes the given job from the task scheduler.

        :param str context_id: Message context id
        :param str job_id: Scheduled Job identifier
        """
        self._scheduler.remove_job(job_id=job_id, jobstore='default')
        self._log.info(f"Ctx={context_id}: Removed job id '{job_id}'")

    def list_jobs(self, context_id):
        """
        List jobs in the task scheduler.

        :param str context_id: Message context id
        :return Any job_list: List of  dictionaries with job details
        """
        self._log.info(f"Ctx={context_id}: Getting jobs list")
        jobs = self._scheduler.get_jobs(jobstore='default')
        job_list = []
        for job in jobs:
            job_item = dict()
            job_item['func'] = job.func.__name__
            job_item['id'] = job.id
            job_item['kwargs'] = job.kwargs
            job_item['next_run_time'] = str(job.next_run_time)
            job_list.append(job_item)
        return job_list

    def stop_scheduler(self):
        """
        Shuts down the scheduler thread
        """
        try:
            self._scheduler.shutdown()
            self._log.info("Scheduler shut down successfully")
        except Exception as e:
            self._log.error(f"<<{type(e).__qualname__}>> {e}")
