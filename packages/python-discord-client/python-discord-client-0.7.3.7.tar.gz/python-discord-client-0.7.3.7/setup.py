#!/usr/bin/python3
# -*- coding:utf-8 -*-
# run via  python3 setup.py upload

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'python-discord-client'
DESCRIPTION = 'Collection of Discord related clients and methods.'
URL = 'https://github.com/btschwertfeger/python-discord-client'
EMAIL = 'development@b-schwertfeger.de'
AUTHOR = 'Benjamin Thomas Schwertfeger'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = None#'0.7.3.2' # 0.7.3.2 was the last

# What packages are required for this module to be executed?
REQUIRED = [
    'requests', 'websockets', 'asyncio>=3.4', 'aiohttp'
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = 'discoPy'
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:  
    raise ValueError('Version not found!')
    exit()

class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f'\033[1m{s}\033[0m')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(f'{sys.executable} setup.py sdist bdist_wheel --universal')

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        # self.status('Pushing git tags…')
        # os.system(f'git tag v{about["__version__"]}')
        # os.system('git push --tags')

        sys.exit()

class TestUploadCommand(Command):
    """Support setup.py test upload."""

    description = 'Build and test publishing the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f'\033[1m{s}\033[0m')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system(f'{sys.executable} setup.py sdist bdist_wheel --universal')

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload -r testpypi dist/*')#--repository-url https://test.pypi.org/legacy/ dist/*')

        sys.exit()

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    cmdclass={
        'upload': UploadCommand,
        'test': TestUploadCommand,
    },
)