from pathlib import Path
from setuptools import setup

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name='divvy-data',
    version='0.0.1',
    description="Methods for loading and monitoring Divvy bikeshare data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/chrisluedtke/divvy-data-analysis",
    packages=['divvydata'],
    author="Chris Luedtke",
    author_email="chrisluedtke@gmail.com",
    install_requires=["lxml", "pandas"],
)
