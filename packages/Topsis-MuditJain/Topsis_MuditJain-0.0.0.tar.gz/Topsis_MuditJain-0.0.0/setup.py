from setuptools import setup, find_packages
import codecs
import os

DESCRIPTION = 'Topsis'
LONG_DESCRIPTION = 'A package to find topsis'

# Setting up
setup(
    name="Topsis_MuditJain",
    version=None,
    author="Mudit Jain",
    author_email="jainmudit67890.md@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)