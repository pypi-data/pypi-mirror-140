from setuptools import setup, find_packages
import codecs
import os

# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

PACKAGE_NAME = 'mchp-flasher-essentials'
VERSION = '0.0.4'
DESCRIPTION = 'Collection of packages required for HB20 Flasher'
NAME = 'HB20 Flasher Essential'
REQUIRED_PACKAGES = [
    'colorama==0.4.4',
    'inputimeout==1.0.4',
    'intelhex==2.3.0',
    'psutil==5.8.0',
    'PyDirectInput==1.0.4',
    'pyelftools==0.27',
    'pywin32==301',
    'termcolor==1.1.0'
]


def read_file(path, encoding='ascii'):
    with open(os.path.join(os.path.dirname(__file__), path),
              encoding=encoding) as fp:
        return fp.read()


# Setting up
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Vazeeruddin (Microchip)",
    author_email="<support@microchip.com>",
    url='https://bitbucket.microchip.com/dashboard',
    license='Microchip',
    description=DESCRIPTION,
    long_description=read_file('README.rst'),
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    keywords=['python', 'HB20', 'flasher', 'medical', 'WSG'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Python :: 3.6",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
