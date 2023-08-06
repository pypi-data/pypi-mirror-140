from setuptools import setup, find_packages
import pathlib
import sys

version = "0.0.2dev"

with open("README.md") as f:
    readme = f.read()

requirements = pathlib.Path().home() / pathlib.Path("repos/DDS/dds_cli/requirements.txt")
print(f"requirements: {requirements}")
if not requirements.exists():
    print(f"requirements not found: {requirements}")
    sys.exit(1)

with requirements.open(mode="r") as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name="dds_cli",
    version=version,
    description="A command line tool to manage data and projects in the SciLifeLab Data Delivery System.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ScilifelabDataCentre/dds_cli",
    license="MIT",
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=["twine>=1.11.0", "setuptools>=38.6.", "wheel"],
    entry_points={
        "console_scripts": [
            "dds = dds_cli.__main__:dds_main",
        ],
    },
    zip_safe=False,
)
