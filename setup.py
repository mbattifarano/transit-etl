from setuptools import setup

with open("requirements.txt") as fp:
    requirements = list(fp)

setup(
    name="transit-etl",
    version='0.0.1-alpha',
    author="Matt Battifarano",
    license="MIT",
    packages=['transit_etl'],
    install_requires=requirements,
    entry_points={
        'console_scripts': ['transit-etl=transit_etl.cli:cli']
    }
)
