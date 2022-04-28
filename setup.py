from setuptools import setup
from setuptools import find_packages

"""Packaging tool for IOCMite"""

from setuptools import setup
from setuptools import find_packages

"""Returns contents of README.md."""
with open("README.md", "r", encoding="utf-8") as readme_fp:
    long_description = readme_fp.read()

setup(
    name="iocmite",
    version="1.0",
    description="Import indicators of different data sources to dataset Suricata and add sightings in MISP on this indicators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
    ],
    keywords="misp suricata datasets",
    url="https://github.com/sebdraven/IOCmite",
    author="Sebastien Larinier @Sebdraven",
    license="Apache",
    packages=["suricata_misp", "scripts", "utils"],
    install_requires=["pymisp", "redis", "tailer", "idstools"],
    entry_points={
        "console_scripts": ["iocmite=scripts.iocmite:main"],
    },
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
)
