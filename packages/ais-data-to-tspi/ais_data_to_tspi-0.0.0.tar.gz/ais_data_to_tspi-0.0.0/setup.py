from setuptools import find_packages, setup

setup(
    name='ais_data_to_tspi',
    packages=find_packages(),
    install_requires=['pandas==1.4.1'],
    description='Generate TSPI text files from AIS data',
    author='Josef Zapletal',
    license='None'
)