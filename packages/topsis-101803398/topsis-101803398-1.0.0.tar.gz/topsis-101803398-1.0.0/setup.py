import pathlib
from setuptools import setup
import codecs
import os

# Location of file directory
HERE = pathlib.Path(__file__).parent

# Readme
README = (HERE / "README.md").read_text()

VERSION = '1.0.0'
DESCRIPTION = 'Topsis implementation'

# Setting up
setup(
    name="topsis-101803398",
    version=VERSION,
    author="Harshit Verma",
    author_email="iamharshitverma114@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url = "https://github.com/HarshitVerma001/topsis-101803398",
    license="MIT",
    long_description=README,
    packages=["topsis"],
    install_requires=["sys", "pandas", "numpy", "os"],
     classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "topsis=topsis.__main__:main",
        ]
    },
)