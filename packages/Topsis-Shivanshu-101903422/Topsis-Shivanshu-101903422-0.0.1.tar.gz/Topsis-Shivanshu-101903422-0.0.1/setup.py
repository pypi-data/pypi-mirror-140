from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Topsis'
LONG_DESCRIPTION = 'A basic programme that may be used in a multi-decision criteria process to assist you choose the best choice from all the options provided.'

# Setting up
setup(
    name="Topsis-Shivanshu-101903422",
    version=VERSION,
    author="Shivanshu Khajuria",
    author_email="<shivanshukhajuria@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[ 'pandas', 'numpy'],
    keywords=['python','numpy','rank','score',],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)