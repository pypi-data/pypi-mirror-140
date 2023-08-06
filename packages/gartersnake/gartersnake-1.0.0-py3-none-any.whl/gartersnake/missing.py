from pathlib import Path
import re
from typing import Dict, List, Mapping, Union

from gartersnake.pip import installed_packages


def read_requirements() -> List[str]:
    requirements_txt_filename = Path('requirements.txt')
    packages = []
    if requirements_txt_filename.exists():
        packages.extend(requirements_txt_filename.open().readlines())
    return packages


def missing_requirements(requirements: Union[List[str], Dict[str, List[str]]] = None) -> Union[List[str], Dict[str, List[str]]]:
    if requirements is None:
        requirements = read_requirements()

    if isinstance(requirements, Mapping):
        missing_packages = missing_requirements(list(requirements))
        missing_dependencies = {}
        for requirement, subrequirements in requirements.items():
            missing_subpackages = missing_requirements(subrequirements)
            if requirement in missing_packages or len(missing_subpackages) > 0:
                missing_dependencies[requirement] = missing_subpackages
        return missing_dependencies
    else:
        return [
            required_package
            for required_package in requirements
            if re.split('<|<=|==|>=|>', required_package)[0].lower()
               not in installed_packages()
        ]
