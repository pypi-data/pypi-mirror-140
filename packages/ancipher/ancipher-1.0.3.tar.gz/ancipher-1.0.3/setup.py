from setuptools import setup, find_packages
import os


VERSION = '1.0.3'
DESCRIPTION = 'Alpha Numeric Cipher aka ancihper'
LONG_DESCRIPTION = ''


# Setting up
setup(
    name="ancipher",
    version=VERSION,
    author="Divinemonk",
    author_email="<v1b7rc8eb@relay.firefox.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url = 'https://github.com/Divinemonk/ancipher/',
    packages=['ancipher'],
    #py_modules = [],
    #install_requires=[''],
    keywords=['python', 'python3', 'cipher', 'ancipher'],
    # include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License"
    ]
)