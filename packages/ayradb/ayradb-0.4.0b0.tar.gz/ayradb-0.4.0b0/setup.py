from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="ayradb",
    version="0.4.0-beta",
    licence="Apache-2.0",
    author="CherryData srl",
    author_email="info@cherry-data.com",
    description="AyraDB python client",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://www.ayradb.com",
    keywords=["AyraDB", "client", "noSQL", "database", "connector", "key-value"],
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    install_requires=[],
    python_requires=">=3.7",
)
