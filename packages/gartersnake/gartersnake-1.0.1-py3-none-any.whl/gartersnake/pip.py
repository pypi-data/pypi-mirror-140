import subprocess
import sys
from typing import List

try:
    from importlib import metadata as importlib_metadata
except ImportError:  # for Python<3.8
    subprocess.run(
        f'{sys.executable} -m pip install importlib_metadata',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    import importlib_metadata


def installed_packages() -> List[str]:
    installed_distributions = importlib_metadata.distributions()
    return [
        distribution.metadata['Name'].lower()
        for distribution in installed_distributions
        if distribution.metadata['Name'] is not None
    ]
