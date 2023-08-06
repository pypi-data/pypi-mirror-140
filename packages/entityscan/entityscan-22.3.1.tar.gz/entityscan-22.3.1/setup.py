import re
from os import path
from pathlib import Path

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    version = Path(package, "__version__.py").read_text()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", version).group(1)


def get_long_description():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
    return long_description


install_requires = [
    "hyperscan==0.2.0",
    "pony==0.7.16",
    "DAWG==0.8.0",
]

setup(
    name="entityscan",
    python_requires=">=3.6",
    version=get_version("src/entityscan"),
    author="Ian Maurer",
    author_email="ian@genomoncology.com",
    packages=find_packages("src/"),
    package_dir={"": "src"},
    package_data={"": ["*.sql"]},
    include_package_data=True,
    # entry_points={"console_scripts": ["entityscan=entityscan:cli"]},
    install_requires=install_requires,
    description="Find entities using Hyperscan",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/genomoncology/entityscan",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
)
