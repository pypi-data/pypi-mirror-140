import subprocess
import sys
from typing import List

from setuptools import config, find_packages, setup

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


try:
    if 'dunamai' not in installed_packages():
        subprocess.run(
            f'{sys.executable} -m pip install dunamai',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    from dunamai import Version

    __version__ = Version.from_any_vcs().serialize()
except (ModuleNotFoundError, RuntimeError) as error:
    print(error)
    __version__ = '0.0.0'

print(f'using version {__version__}')

metadata = config.read_configuration('setup.cfg')['metadata']

setup(
    **metadata,
    version=__version__,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    setup_requires=['dunamai', 'setuptools>=41.2'],
    install_requires=[],
    extras_require={
        'testing': ['pytest', 'pytest-cov', 'pytest-xdist', 'wget'],
        'development': ['flake8', 'isort', 'oitnb'],
    },
)
