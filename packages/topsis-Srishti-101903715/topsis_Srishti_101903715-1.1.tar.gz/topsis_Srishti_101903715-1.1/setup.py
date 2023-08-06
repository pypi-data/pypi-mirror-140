# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_Srishti_101903715",
    version="1.1",
    description="A Python package to rank ML models/choices using topsis technique",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Srishti Vermani",
    author_email="ssrishti_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_Srishti_101903715"],
    include_package_data=True,
    install_requires=["pandas"],
)
