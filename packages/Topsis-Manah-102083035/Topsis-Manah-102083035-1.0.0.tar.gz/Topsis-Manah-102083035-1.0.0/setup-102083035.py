import os
from setuptools import setup

NAME = "Topsis-Manah-102083035"
VERSION = "1.0.0"
DESCRIPTION = "A package for topsis score generation."
AUTHOR = "Manah Verma"
AUTHOR_EMAIL = "mverma_be19@thapar.edu"
PACKAGES_PRESENT = ['Topsis-Manah-102083035']
PACKAGES_NEED = ['pandas','numpy']

def read_file(name):
    path = os.getcwd()
    return open(f"{path}\{name}").read()

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    description = DESCRIPTION,
    packages = PACKAGES_PRESENT,
    install_requires = PACKAGES_NEED,
    # long_description=read_file('README.md'),
    # long_description_content_type='text/markdown',
    license = read_file('LICENSE.md')
)

