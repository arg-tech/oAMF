# Setup script for making oAMF installable
import os
import yaml
import subprocess
import shutil
from setuptools import setup, find_packages
setup(
    name='oAMF',
    version='1.0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML',
        'networkx',  # Add networkx dependency
        'pandas',    # Add pandas dependency
    ],
    entry_points={
        'console_scripts': [
            'oamf = oamf:main'
        ]
    },
    description='oAMF pipeline manager',
    author='Debela',
    author_email='dabookoo@gmail.com',
    url='https://github.com/arg-tech/oAMF',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

# Usage example (after installation):
# from oamf import oAMF
# metadata_file = "path_to_oamf_metadata.yml"
# pipeline_modules = ["project-a", "project-b"]
# manager = oAMF(metadata_file)
# manager.install_pipeline(pipeline_modules)
