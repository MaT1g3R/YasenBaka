import re
from os import getpid
from pathlib import Path
from platform import release, system

from psutil import Process, virtual_memory

try:
    from distro import linux_distribution
except ImportError:
    linux_distribution = None


def ram_usage() -> float:
    """
    Get memory usage by this process in MiB.
    :return: the memory usage in MiB.
    """
    py = Process(getpid())
    return float(py.memory_info().rss) / 1024 / 1024


def total_ram() -> float:
    """
    Get total system memory in MiB.
    :return: total system memory in MiB
    """
    return float(virtual_memory().total) / 1024 / 1024


def __sys_name():
    """
    Fallback function to get system name.
    :return: System name from /etc/issue if the file exists else system release
    """
    path = Path('/etc/issue')
    fallback = f'{system()} {release()}'
    if path.is_file():
        with Path('/etc/issue').open() as f:
            raw = f.readline().strip().split(' ')
            regex = re.compile('[\w^[\\]]+')
            res = ' '.join((s for s in raw if regex.fullmatch(s)))
            return res or fallback
    return fallback


def system_name() -> str:
    """
    Get the current system name.
    :return: the current system name.
    """
    if not linux_distribution:
        return __sys_name()
    return ' '.join((s.title() for s in linux_distribution(False)))
