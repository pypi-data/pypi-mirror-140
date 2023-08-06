import setuptools
from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

NAME = 'respec'
VERSION = '0.0.1'
URL = 'https://github.com/SSripilaipong/respec'
LICENSE = 'MIT'
AUTHOR = 'SSripilaipong'
EMAIL = 'SHSnail@mail.com'

setup(
    name=NAME,
    version=VERSION,
    packages=[package for package in setuptools.find_packages() if not package.startswith('tests.')],
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=None,
    long_description=None,
    python_requires='>=3.10',
    install_requires=requirements,
    classifiers=[],
)
