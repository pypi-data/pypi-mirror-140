from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Topsis'

# Setting up
setup(
    name="Topsis_1823",
    version=VERSION,
    author="Shriyanshi Agarwal",
    author_email="<shriyanshi2301@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy','pandas'],
    keywords=['topsis','python', 'model', 'best', 'test'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)