from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.13'
DESCRIPTION = 'short hello description'
LONG_DESCRIPTION = 'simple hello long desc'

# Setting up
setup(
    name="Topsis-Kunal-101917017",
    version=VERSION,
    author="Kunal pathak",
    author_email="<kpathak_be19@thapar.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'hello'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)