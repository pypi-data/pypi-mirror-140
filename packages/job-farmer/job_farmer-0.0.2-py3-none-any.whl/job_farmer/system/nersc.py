from .system import System
from typing import List


class CoriHaswell(System):
    def __init__(self):
        """
        Constructor for the Cori-Haswell system
        """
        super().__init__(system_name='cori-haswell',
                         physical_cpu_cores_per_node=32,
                         threads_per_cpu_core=2,
                         physical_gpu_per_node=0,
                         memory_per_node_gb=128,
                         queues=['regular', 'shared', 'interactive', 'debug', 'premium', 'flex'])

    def get_constrains(self) -> List[str]:
        constrains = ['#SBATCH -C haswell']
        return constrains


class CoriKNL(System):
    def __init__(self):
        """
        Constructor for the Cori-KNL system
        """
        super().__init__(system_name='cori-knl',
                         physical_cpu_cores_per_node=64,
                         threads_per_cpu_core=4,
                         physical_gpu_per_node=0,
                         memory_per_node_gb=96,
                         queues=['regular', 'interactive', 'debug', 'premium', 'low', 'flex'])

    def get_constrains(self) -> List[str]:
        constrains = ['#SBATCH -C knl']
        return constrains


class Perlmutter(System):
    def __init__(self):
        """
        Constructor for the Perlmutter system
        """
        super().__init__(system_name='perlmutter',
                         physical_cpu_cores_per_node=64,
                         threads_per_cpu_core=2,
                         physical_gpu_per_node=4,
                         memory_per_node_gb=256,
                         queues=['regular', 'interactive', 'debug'])

    def get_constrains(self) -> List[str]:
        constrains = ['#SBATCH -C gpu']
        return constrains

