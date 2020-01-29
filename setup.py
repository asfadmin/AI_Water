"""
While in the root directory run "pip install -e .".
This will install AI_Water as a package, and create the models and datasets directory.
"""

from setuptools import find_packages, setup
import os

setup(name='AI_Water', version='1.0', packages=find_packages())

if not os.path.isdir('datasets'):
    os.mkdir('datasets')
if not os.path.isdir('models'):
    os.mkdir('models')