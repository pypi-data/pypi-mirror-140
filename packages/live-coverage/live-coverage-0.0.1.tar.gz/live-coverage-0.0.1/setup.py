from setuptools import setup, find_packages
from os import environ

setup(
    name="live-coverage",
    version="0.0.1",
    url="https://github.com/Defelo/live-coverage",
    author="Defelo",
    author_email="elodef42@gmail.com",
    description="Live Code Coverage for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["live-coverage=live_coverage.live_coverage:main"]},
)
