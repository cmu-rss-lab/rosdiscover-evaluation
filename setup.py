# -*- coding: utf-8 -*-
import os
from glob import glob
from setuptools import setup, find_packages
path = os.path.join(os.path.dirname(__file__), 'scripts/version.py')
with open(path, 'r') as f:
    exec(f.read())


setup(
    version=__version__,
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'list=scripts/list_experiments:main',
            'build-images=scripts/build-images:main',
            'check=scripts/check-architecture.py',
            'compare=scripts/compare-recoverd-observed.py',
            'observe=scripts/observe-system.py',
            'recover-node-models=scripts/recover-node-models.py',
            'recover=scripts/recover-system.py'
        ]
    },
   test_suite='test')
