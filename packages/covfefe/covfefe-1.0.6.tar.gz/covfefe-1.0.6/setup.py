
import sys

from distutils.core import setup
from distutils.core import Extension

requirements = []
test_requirements = []

setup(
    name='covfefe',
    version='1.0.6',
    license='MIT',
    author="Ee Durbin",
    author_email='ewdurbin@gmail.com',
    description='dope project i started and never finished',
    url='https://github.com/ewdurbin/covfefe',
    packages=['covfefe'],
    scripts=[],
    install_requires=requirements,
    tests_require=test_requirements,
)

