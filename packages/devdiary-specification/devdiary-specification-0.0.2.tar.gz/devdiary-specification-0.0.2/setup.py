import setuptools
from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

NAME = 'devdiary-specification'
VERSION = '0.0.2'
URL = 'https://github.com/SSripilaipong/DevDiary/tree/main/specification'
LICENSE = 'MIT'
AUTHOR = 'SSripilaipong'
EMAIL = 'SHSnail@mail.com'

setup(
    name=NAME,
    version=VERSION,
    packages=[package for package in setuptools.find_packages() if package.startswith('devdiary.specification.')],
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=None,
    long_description=None,
    python_requires='>=3.7',
    install_requires=requirements,
    classifiers=[],
)
