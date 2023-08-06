"""Module for creating installer."""
import setuptools

long_description = """This module is created in order to simplify the process of copying the SSM documents from one region to another regions.

* As an organisation or team can have multiple regions in which they operate. And in order to replicate the SSM documents from one region to another.

* It becomes a tedious task if you are developing or if you need to update a document and replicate the change across the regions.

* To resolve this issue, ssm-cloner comes for your help.

* Just execute this module and pass on the parameters and it will clone the documents for you.

* You can also use it to unclone or create new version for your documents."""

setuptools.setup(
    name="ssm-cloner",
    version="0.0.1",
    author="Love Purohit",
    author_email="lvpurohit1@gmail.com",
    description="(Not to be used as of now) This package is used to simplify the process of cloning the SSM documents across the AWS regions.",
    long_description=long_description,
    url="https://github.com/lovepurohit/ssm-cloner",
    project_urls={
        "Bug Tracker": "https://github.com/lovepurohit/ssm-cloner/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=['boto3'],
    python_requires=">=3.6",
)
