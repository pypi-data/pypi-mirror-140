import codecs
import os
import re

import setuptools
from pkg_resources import parse_requirements


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), "r") as fp:
        version_file = fp.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(f_name: str) -> list:
    requirements = []
    with open(f_name, "r") as fp:
        for req in parse_requirements(fp.read()):
            extras = "[{}]".format(",".join(req.extras)) if req.extras else ""
            requirements.append("{}{}{}".format(req.name, extras, req.specifier))  # type:ignore
    return requirements


setuptools.setup(
    name="mb-waves",
    version=find_version("mb_waves/__init__.py"),
    python_requires=">=3.10",
    packages=["mb_waves"],
    install_requires=[
        "click~=8.0.4",
        "click-aliases~=1.0.1",
        "PyWaves==0.8.42",
        "mb-std~=0.3",
    ],
    extras_require={
        "dev": [
            "pytest==7.0.1",
            "pytest-xdist==2.5.0",
            "pre-commit==2.17.0",
            "wheel==0.37.1",
            "twine==3.8.0",
            "pip-audit==2.0.0",
        ],
    },
    entry_points={"console_scripts": ["mb-waves = mb_waves.cli.cmd:cli"]},
    include_package_data=True,
)
