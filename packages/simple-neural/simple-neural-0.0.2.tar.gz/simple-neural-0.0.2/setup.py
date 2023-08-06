import os
import pathlib
from setuptools import setup
from setuptools import find_packages
from simplenn import __version__

try:
    # pip >=20
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.req import parse_requirements
    except ImportError:
        import re
        from dataclasses import dataclass

        def parse_requirements(f, *args, **kwargs):
            @dataclass
            class Req:
                requirement: str

            requirements = []
            for line in open(f, "r").read().split("\n"):
                if re.match(r"(\s*#)|(\s*$)", line):
                    continue
                if re.match(r"\s*-e\s+", line):
                    requirements.append(re.sub(r"\s*-e\s+.*#egg=(.*)$", r"\1", line))
                elif re.match(r"\s*-f\s+", line):
                    pass
                else:
                    requirements.append(Req(line))
            return requirements


def load_requirements(fname):
    """Parse requirements.txt file"""
    requirements = list(parse_requirements(fname, session="test"))
    parsed_reqs = []
    for r in requirements:
        try:
            value = getattr(r, "req")
            if value is None:
                raise AttributeError
            parsed_reqs.append(value)
        except AttributeError:
            parsed_reqs.append(r.requirement)
    return parsed_reqs


REQUIREMENTS_FILE = os.path.join(str(pathlib.Path(__file__).parent.resolve()), "requirements.txt")
BUILD_DEPENDENCIES = ["wheel"]
DEPENDENCIES = BUILD_DEPENDENCIES + load_requirements(REQUIREMENTS_FILE)

setup(
    name="simple-neural",
    version=__version__,
    description="Simple Deep Learning Framework",
    author="Roberto Crespo",
    author_email="ra.crespoa@gmail.com",
    packages=find_packages("."),
    install_requires=DEPENDENCIES,
)
