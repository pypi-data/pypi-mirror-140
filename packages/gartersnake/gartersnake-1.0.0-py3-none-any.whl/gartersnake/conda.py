from pathlib import Path
import subprocess
import sys
from typing import List

from gartersnake.missing import missing_requirements


def is_conda() -> bool:
    return (Path(sys.prefix) / 'conda-meta').exists()


def install_conda_requirements(requirements: List[str] = None, overwrite: bool = False):
    if is_conda():
        print(f'found conda environment at {sys.prefix}')
    else:
        raise EnvironmentError('conda environment not detected')

    if overwrite:
        missing_packages = requirements
    else:
        missing_packages = missing_requirements(requirements)

    conda_packages = []
    try:
        subprocess.check_output(
            f'conda install -y {" ".join(missing_packages)}',
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as error:
        output = error.output.decode()
        package_not_found_start = 'PackagesNotFoundError: The following packages are not available from current channels:\n\n'
        package_not_found_stop = '\n\nCurrent channels:'
        if package_not_found_start in output:
            non_conda_packages = [
                package.strip()
                for package in output[
                               output.index(package_not_found_start): output.index(
                                   package_not_found_stop
                               )
                               ].splitlines()[2:]
            ]
            conda_packages = [
                package
                for package in missing_packages
                if not any(non_conda_package in package for non_conda_package in non_conda_packages)
            ]

            print(
                f'found {len(conda_packages)} conda packages (out of {len(missing_packages)}) - {conda_packages}'
            )

    try:
        subprocess.run(
            f'conda install -y {" ".join(conda_packages)}',
            shell=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print('batch install failed; attempting individual installs...')
        for dependency in conda_packages:
            try:
                subprocess.run(
                    f'conda install -y {dependency}', shell=True, stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError:
                continue
