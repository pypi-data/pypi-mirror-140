from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with open('requirements.txt') as f:
    required = f.read().splitlines()

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'A clustering based approach to inferring the use case of an ' \
              'intelligent contact. Developed by A3Data, packaged by D&A ' \
              'Research - Take Blip.'


# Setting up
setup(
    name="take-icusecases",
    version=VERSION,
    author='A3Data / Data & Analytics Research',
    license='MIT License',
    credits=['Gustavo Resende', 'Ramon Durães'],
    maintainer="daresearch",
    author_email='<analytics.dar@take.net>',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=required,
    keywords=['take blip', 'intelligent contact', 'use cases', 'clustering'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
