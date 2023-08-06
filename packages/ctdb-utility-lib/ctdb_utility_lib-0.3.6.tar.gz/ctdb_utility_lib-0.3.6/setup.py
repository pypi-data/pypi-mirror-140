from setuptools import find_packages, setup

setup(
    name="ctdb_utility_lib",
    packages=find_packages(include=["ctdb_utility_lib"]),
    version="0.3.6",
    description="Contact Tracer DB Utility Python library",
    install_requires=["psycopg2"],
    author="[Ahmed, Dylan]",
    license="MIT",
)
