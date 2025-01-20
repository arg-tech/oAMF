# Setup script for making oAMF installable
import os
import yaml
import subprocess
import shutil
from setuptools import setup, find_packages
setup(
    name='oAMF',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'oamf = oamf:main'
        ]
    },
    description='oAMF pipeline manager',
    author='Your Name',
    author_email='your_email@example.com',
    url='https://github.com/your-repo/oamf',
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
