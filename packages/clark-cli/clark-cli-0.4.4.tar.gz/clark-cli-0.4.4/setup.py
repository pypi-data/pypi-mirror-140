import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command

# Package meta-data.
NAME = 'clark-cli'
PACKAGE = 'clark'
DESCRIPTION = 'A tool which auto-documents researcher workflows.'
URL = 'https://github.com/Elio-Earth/clark-cli'
EMAIL = 'tech@elio.earth'
AUTHOR = 'Elio Engineering'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None
LICENSE = 'GPLv3'
REQUIRED = [
    'click>=8.0.1',
    'requests>=2.26.0',
    'boto3>=1.20.0',
    'colorama>=0.4.4'
]

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
if not VERSION:
    with open(os.path.join(here, PACKAGE, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

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
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(about['__version__']))
        os.system('git push --tags')

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
    packages=['clark'],
    entry_points={
        'console_scripts': ['clark=clark.main:main'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)