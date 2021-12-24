#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

setup_requirements = [
]

test_requirements = [
]

setup(
    name='clickable_igloo',
    version="1.1",
    description=("Igloo helpers for clickable."),
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    author="Laurent Almeras",
    author_email='lalmeras@gmail.com',
    url='https://github.com/lalmeras/clickable_igloo',
    packages=find_packages(include=['clickable_igloo', 'clickable_igloo.*']),
    entry_points={
        'console_scripts': [
        ]
    },
    include_package_data=True,
    install_requires=[
        "clickable >= 1.5"
    ],
    python_requires='>=3.6',
    license="BSD license",
    zip_safe=False,
    keywords='clickable',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
