from typing import List


class System:

    def __init__(self,
                 system_name: str = "Default",
                 physical_cpu_cores_per_node: int = 0,
                 threads_per_cpu_core: int = 0,
                 physical_gpu_per_node: int = 0,
                 memory_per_node_gb: int = 0,
                 queues: List[str] = None
                 ):
        """
        Constructor for the system
        :param system_name:
        :param physical_cpu_cores_per_node:
        :param threads_per_cpu_core:
        :param physical_gpu_per_node:
        :param memory_per_node_gb:
        :param queues:
        """
        self.__system_name = system_name
        self.__physical_cpu_cores_per_node = physical_cpu_cores_per_node
        self.__threads_per_cpu_core = threads_per_cpu_core
        self.__physical_gpu_per_node = physical_gpu_per_node
        self.__memory_per_node_gb = memory_per_node_gb
        self.__queues = queues

    @property
    def name(self) -> str:
        return self.__system_name

    @property
    def physical_cpu_cores_per_node(self) -> int:
        return self.__physical_cpu_cores_per_node

    @property
    def threads_per_cpu_core(self) -> int:
        return self.__threads_per_cpu_core

    @property
    def threads_per_node(self) -> int:
        return self.__physical_cpu_cores_per_node * self.__threads_per_cpu_core

    @property
    def memory_per_node_gb(self) -> float:
        return self.__memory_per_node_gb

    @property
    def queues(self) -> List[str]:
        return self.__queues

    def __str__(self) -> str:
        return f'System<{self.__system_name}>'

    def get_constrains(self) -> List[str]:
        return []
