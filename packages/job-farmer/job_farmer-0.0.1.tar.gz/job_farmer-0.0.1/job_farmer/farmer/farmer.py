from functools import reduce
import json
import logging
import math as m
import os
import subprocess
from typing import List, Tuple

from ..system import System
from ..job import JobConfiguration
from ..task import Task


class Farmer:

    def __init__(self,
                 system: System,
                 job_configuration_directory: str = f'{os.getcwd()}/job'):
        """
        Constructor of the farmer
        :param system:
        :param job_configuration_directory:
        """
        self.__system = system
        self.__job_configuration_directory = job_configuration_directory

        self.log = logging.getLogger(f'farmer-{self.__system.name}')
        self.__jobs = {}

        self.log.info(f'Initializing the farmer for the system: {self.__system}')

    @property
    def system(self) -> System:
        """

        :return:
        """
        return self.__system

    def __str__(self) -> str:
        """

        :return:
        """
        return f'Farmer<system:{self.__system.name}, n_jobs:{len(self.__jobs)}>'

    def add_global_job_configuration(self, global_job_configuration: JobConfiguration) -> None:
        """
        Add a new job
        :param global_job_configuration:
        :return:
        """
        self.log.info(f'Adding the job: "{global_job_configuration.name}"')

        if global_job_configuration.name in self.__jobs:
            raise Exception(f'The job configuration "{global_job_configuration.name}" already exists')

        if global_job_configuration.queue not in self.__system.queues:
            raise Exception(
                f'The job configuration "{global_job_configuration.name}" '
                f'uses the queue "{global_job_configuration.queue}" '
                f'which is not available for {self.__system}. Available options are:'
                f'{self.__system.queues}')

        self.__jobs[global_job_configuration.name] = {'global_job_configuration': global_job_configuration, 'tasks': []}

    def add_task(self, global_job_name: str, task: Task) -> None:
        """

        :param global_job_name:
        :param task:
        :return:
        """
        if global_job_name not in self.__jobs:
            raise Exception(f'The global job configuration "{global_job_name}" is not available. Options are:'
                            f'{list(self.__jobs.keys())}')

        self.__jobs[global_job_name]['tasks'].append(task)

    def add_tasks(self, global_job_name: str, tasks: List[Task]) -> None:
        """

        :param global_job_name:
        :param tasks:
        :return:
        """
        for task in tasks:
            self.add_task(global_job_name, task)

    def build(self) -> None:
        """

        :return:
        """
        for job_name in self.__jobs.keys():
            self.log.info(f'Preparing the job {job_name}:')

            formatted_job_name = job_name.replace(' ', '_')
            slurm_directory, task_list_directory, logs_directory = Farmer.get_folders(
                f'{self.__job_configuration_directory}/{formatted_job_name}')

            global_job_configuration = self.__jobs[job_name]['global_job_configuration']
            global_job_configuration_dict = global_job_configuration.as_dict(drop_node_conf=True)

            job_tasks = self.__jobs[job_name]['tasks']

            max_threads_per_job = self.__system.threads_per_node * global_job_configuration.max_node_per_job

            split_tasks = [[]]
            current_job_threads = 0

            for task in job_tasks:
                if current_job_threads + task.n_threads > max_threads_per_job:
                    split_tasks.append([])
                    current_job_threads = 0

                split_tasks[-1].append(task)
                current_job_threads += task.n_threads

            self.log.info(f'  - n_jobs: {len(split_tasks)}')

            self.__jobs[job_name]['slurm_filenames'] = []
            self.__jobs[job_name]['tasks_filenames'] = []

            for i, tasks in enumerate(split_tasks):
                n_threads = reduce(lambda accumulator, _task: accumulator + _task.n_threads, tasks, 0)
                n_nodes = int(m.ceil(n_threads / self.__system.threads_per_node))
                n_tasks = len(tasks)
                n_thread_per_task = int(n_threads / n_tasks)

                local_job_configuration = JobConfiguration(**global_job_configuration_dict,
                                                           n_threads=n_threads,
                                                           n_nodes=n_nodes,
                                                           n_tasks=n_tasks,
                                                           n_thread_per_task=n_thread_per_task
                                                           )

                self.log.info(f'  - sub-job {i} - n_threads:{n_threads}, n_nodes:{n_nodes}')

                task_list_filename = f'{task_list_directory}/task_list_{job_name}_{i}.py'
                job_script_filename = f'{slurm_directory}/slurm_{job_name}_{i}.sh'

                self.__jobs[job_name]['tasks_filenames'].append(task_list_filename)
                self.__jobs[job_name]['slurm_filenames'].append(job_script_filename)

                Farmer.__build_task_list(task_list_filename, tasks)
                Farmer.__build_job_script(system=self.__system,
                                          job_configuration=local_job_configuration,
                                          job_script_filename=job_script_filename,
                                          task_list_filename=task_list_filename,
                                          logs_directory=logs_directory)

    def submit(self, dry_run: bool = True):

        if dry_run:
            self.log.info('No Automatic job submission, the sbatch command will be printed for your convinience')
        else:
            self.log.info('Automatic job submission')

        for job_name in self.__jobs.keys():

            sbatch_commands = [f'sbatch {slurm_file}' for slurm_file in self.__jobs[job_name]['slurm_filenames']]
            sbatch_commands_str = '\n'.join(sbatch_commands)
            self.log.info(f'For the job: {job_name}:\n{sbatch_commands_str}')

            if not dry_run:
                process = subprocess.Popen(' && '.join(sbatch_commands), shell=True)
                process.communicate()
                exit_code = process.wait()
                return exit_code

    @staticmethod
    def get_folders(job_configuration_directory: str) -> Tuple[str, str, str]:
        """

        :param job_configuration_directory:
        :return:
        """
        slurm_configuration_directory = f'{job_configuration_directory}/slurm'
        task_list_directory = f'{job_configuration_directory}/task_list'
        logs_directory = f'{job_configuration_directory}/logs'

        os.makedirs(slurm_configuration_directory, exist_ok=True)
        os.makedirs(task_list_directory, exist_ok=True)
        os.makedirs(logs_directory, exist_ok=True)

        return slurm_configuration_directory, task_list_directory, logs_directory

    @staticmethod
    def __build_task_list(task_list_filename: str, tasks: List[Task]) -> None:
        """

        :param task_list_filename:
        :param tasks:
        :return:
        """
        task_list = open(task_list_filename, 'w')
        tasks_json = json.dumps(tasks, default=Task.json_encoder, indent=4).replace('null', 'None')
        task_list.write(f'tasks = {tasks_json}')

        task_list.close()

    @staticmethod
    def __build_job_script(system: System,
                           job_configuration: JobConfiguration,
                           job_script_filename: str,
                           task_list_filename: str,
                           logs_directory: str) -> None:

        def check_node_value(__job_configuration: JobConfiguration, variable_mame: str) -> int:
            """
            Check the values an
            :param __job_configuration:
            :param variable_mame:
            :return:
            """
            value = getattr(__job_configuration, variable_mame)
            if value > 0:
                return value
            else:
                raise Exception(f'Job configuration incorrect value for the variable {variable_mame}.')

        n_nodes = check_node_value(job_configuration, 'n_nodes')
        n_tasks = check_node_value(job_configuration, 'n_tasks')
        n_thread_per_task = check_node_value(job_configuration, 'n_thread_per_task')

        job_script = ['#!/bin/bash',
                      f'#SBATCH -J {job_configuration.name}',
                      f'#SBATCH -A {job_configuration.account}',
                      f'#SBATCH -t {job_configuration.duration}',
                      f'#SBATCH -N {n_nodes}',
                      f'#SBATCH -q {job_configuration.queue}',
                      f'#SBATCH --output={logs_directory}/slurm-%x_%j_%t.out',
                      f'#SBATCH --error={logs_directory}/slurm-%x_%j_%t.err',
                      '']

        job_script.extend(system.get_constrains())
        job_script.extend(job_configuration.get_extra_configuration())

        dir_path = os.path.dirname(os.path.realpath(__file__))
        runner_path = os.path.abspath(f'{dir_path} /../../job_runner/job_runner.py')

        srun_comd = ['',
                     'module load python',
                     f'srun -n {n_tasks} -c {n_thread_per_task} python {runner_path} --task-list {task_list_filename}']

        job_script.extend(srun_comd)

        job_script_file = open(job_script_filename, 'w')

        job_script_file.write('\n'.join(job_script))
        job_script_file.write('\n')

        job_script_file.close()
