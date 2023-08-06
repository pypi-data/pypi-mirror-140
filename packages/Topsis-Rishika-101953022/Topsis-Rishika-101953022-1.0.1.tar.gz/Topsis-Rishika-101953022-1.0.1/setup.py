from setuptools import setup, find_packages
import codecs
import os

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="Topsis-Rishika-101953022",
    version="1.0.1",
    description="A Python package for topsis analysis.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Rishika",
    author_email="rishikatayal2325@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    install_requires=[]
) 