from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="testwizard.core",
    version="3.6.0",
    author="Eurofins Digital Testing - Belgium",
    author_email="testwizard-support@eurofins-digitaltesting.com",
    description="Testwizard core",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.eurofins-digitaltesting.com/testwizard/",
    packages=find_namespace_packages(),
    install_requires=[
          'jsons',
          'testwizard.commands-core==3.6.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)
