#!/usr/bin/env python
"""Distribution configuration."""

from setuptools import setup, find_packages

setup(
    name='voxcell',
    author="Blue Brain Project, EPFL",
    description='Voxcell is a small library to handle probability'
                ' distributions that have a spatial component and to use them'
                ' to build collection of cells in space.',
    url="https://github.com/BlueBrain/voxcell",
    download_url="https://github.com/BlueBrain/voxcell",
    license='Apache-2',
    install_requires=[
        'h5py>=3.1.0',
        'numpy>=1.9',
        'pandas>=0.24.2',
        'pynrrd>=0.4.0',
        'requests>=2.18',
        'scipy>=1.2.0',
    ],
    packages=find_packages(),
    python_requires='>=3.7',

    use_scm_version={
        "local_scheme": "no-local-version",
        },
    setup_requires=[
        'setuptools_scm',
    ],

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
