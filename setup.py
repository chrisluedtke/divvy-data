from pathlib import Path
from setuptools import setup, find_packages

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name='divvy',
    version='0.1',
    description="Methods for loading and monitoring Divvy bikeshare data",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Chris Luedtke",
    install_requires=["lxml", "pandas"],
)
