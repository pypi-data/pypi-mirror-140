#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
import bsb
import os


def path_in_project(*path):
    return os.path.join(os.path.dirname(__file__), *path)


def read_file(filename):
    with open(path_in_project(filename)) as f:
        return f.read()


def read_requirements(filename):
    contents = read_file(filename).strip('\n')
    return contents.split('\n') if contents else []


if sys.version_info[:3] < (3, 6, 1):
    raise Exception("Coffin Codes requires Python >= 3.6.1.")

description = 'BSB-Developers'
long_description = read_file('README.md')

setup(
    name='Coffin-Codes-Pro',
    version="7.0",
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='BSB-Developers Coffin Codes V7',
    author='BSB-Developers',
    author_email='sphabsb2192@yahoo.com',
    maintainer='SphaBSB',
    maintainer_email='sphabsb2192@yahoo.com',
    url='https://github.com/azimjohn/jprq-py',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bsb = bsb.main:main',
        ]
    },
    install_requires=read_requirements('requirements.txt'),
    python_requires='>=3.6.1',
)
