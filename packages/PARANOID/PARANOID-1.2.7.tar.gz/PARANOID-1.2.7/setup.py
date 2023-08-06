import codecs
import os
import shutil

from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


if not os.path.exists('scripts'):
    os.makedirs('scripts')
shutil.copyfile('src/paranoid.py', 'scripts/paranoid')
from src.version import version

setup(
    name='PARANOID',
    version=version,
    url='https://gitlab.com/sonra-labs/paranoid',
    license='Apache Software License',
    author='Sonra Intelligence Ltd',
    author_email='hello@sonra.io',
    description='A utility to obfuscate and mask elements in XML and JSON files',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires='>=2.6, >=2.6.*,>=2.7.*, <4',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    packages=find_packages(include=['paranoid', 'timestamp_validator_27', 'timestamp_validator_3', "version", 'src']),
    entry_points={
        'console_scripts': [
            'paranoid = src.paranoid:main'
        ]
    }
)
