# Copyright (C) 2021 Matthias Nadig

from setuptools import setup, find_packages


with open('README.md', 'r') as f:
    long_description = f.read()

path_package_toplevel = 'src'

setup(
    name='ndbounds',
    version='4.0.0',
    description='Toolbox for handling n-dimensional bounds',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Matthias Nadig',
    author_email='matthias.nadig@yahoo.com',
    license='MIT',
    package_dir={'': path_package_toplevel},
    packages=find_packages(where=path_package_toplevel),
    python_requires='>=3.4',
    install_requires=['numpy'],
)
