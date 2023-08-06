# -*- coding: utf-8 -*-

from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="topsis_Nandini_101903480",
    version="1.1",
    description="A Python package to rank ML models/choices using topsis technique",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nandiniseth0809/topsis-nandini-101903480",
    author="Nandini Seth",
    author_email="nandiniseth0809@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["topsis_Nandini_101903480"],
    include_package_data=True,
    install_requires=["pandas"],
)
