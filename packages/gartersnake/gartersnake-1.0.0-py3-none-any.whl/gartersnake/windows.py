import os
import subprocess
import sys
from typing import Dict, List, Mapping, Union

from gartersnake.missing import missing_requirements, read_requirements
from gartersnake.pip import installed_packages


def is_windows() -> bool:
    return os.name == 'nt'


def install_windows_requirements(requirements: Union[List[str], Dict[str, List[str]]] = None, overwrite: bool = False):
    if not is_windows():
        raise EnvironmentError('Windows environment not detected')

    if requirements is None:
        requirements = read_requirements()

    if not isinstance(requirements, Mapping):
        requirements = {requirement: [] for requirement in requirements}

    if overwrite:
        missing_packages = requirements
    else:
        missing_packages = missing_requirements(requirements)

    print(f'attempting to install {len(missing_packages)} packages with `pipwin`')

    if 'pipwin' not in installed_packages():
        raise ImportError('Windows detected but `pipwin` is not installed. Please install `pipwin` to continue.')

    subprocess.run(f'{sys.executable} -m pipwin refresh', shell=True)

    for requirement, subrequirements in missing_packages.items():
        failed_pipwin_packages = []

        # since we don't know the dependencies here, repeat this process n number of times
        # (worst case is `O(n)`, where the first package is dependent on all the others)
        for _ in range(1 + len(subrequirements)):
            for package_name in subrequirements + [requirement]:
                if requirement in missing_requirements(
                        requirements
                ) or package_name in missing_requirements(subrequirements):
                    try:
                        subprocess.run(
                            f'{sys.executable} -m pip install {package_name.lower()}',
                            check=True,
                            shell=True,
                            stderr=subprocess.DEVNULL,
                        )
                        if package_name in failed_pipwin_packages:
                            failed_pipwin_packages.remove(package_name)
                    except subprocess.CalledProcessError:
                        try:
                            subprocess.run(
                                f'{sys.executable} -m pipwin install {package_name.lower()}',
                                check=True,
                                shell=True,
                                stderr=subprocess.DEVNULL,
                            )
                        except subprocess.CalledProcessError:
                            failed_pipwin_packages.append(package_name)

            if len(failed_pipwin_packages) == 0:
                break
