import logging
from typing import List


class JobConfiguration:
    def __init__(self,
                 name: str,
                 account: str,
                 queue: str,
                 duration: str,
                 max_nodes_per_job: int = 1000,
                 use_open_np: bool = False,
                 n_threads: int = -1,
                 n_nodes: int = -1,
                 n_tasks: int = -1,
                 n_thread_per_task: int = -1
                 ):
        """
        Job configuration constructor
        :param name:
        :param account:
        :param queue:
        :param duration:
        :param max_nodes_per_job:
        :param use_open_np:
        :param n_threads:
        :param n_nodes:
        :param n_tasks:
        :param n_thread_per_task:
        """
        self.__name = name
        self.__account = account
        self.__queue = queue
        self.__duration = duration
        self.__max_nodes_per_job = max_nodes_per_job
        self.__use_open_np = use_open_np
        self.__n_threads = n_threads
        self.__n_nodes = n_nodes
        self.__n_tasks = n_tasks
        self.__n_thread_per_task = n_thread_per_task

    def as_dict(self, drop_node_conf: bool = False) -> dict:
        """
        Return the job configuration as a dictionary
        :return:
        """
        dictionary = {}
        for key, value in vars(self).items():
            key = key.replace(f'_{self.__class__.__name__}__', '')
            if drop_node_conf and key in ['n_threads', 'n_nodes', 'n_tasks', 'n_thread_per_task']:
                continue
            dictionary[key] = value

        return dictionary

    @property
    def name(self):
        return self.__name

    @property
    def account(self):
        return self.__account

    @property
    def queue(self):
        return self.__queue

    @property
    def duration(self):
        return self.__duration

    @property
    def max_node_per_job(self):
        return self.__max_nodes_per_job

    @property
    def n_threads(self):
        return self.__n_threads

    @property
    def n_nodes(self):
        return self.__n_nodes

    @property
    def n_tasks(self):
        return self.__n_tasks

    @property
    def n_thread_per_task(self):
        return self.__n_thread_per_task

    def get_extra_configuration(self) -> List[str]:
        extra_config = []

        if self.__use_open_np:
            extra_config.extend(JobConfiguration.get_open_mp())

        return extra_config

    @staticmethod
    def get_open_mp():

        open_mp_config = []

        return open_mp_config
