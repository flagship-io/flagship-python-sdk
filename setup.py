import setuptools
from flagship import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='flagship',
    version=__version__,
    author="Flagship Team",
    author_email="support@flagship.io",
    description="Flagship Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abtasty/flagship-python-sdk",
    packages=setuptools.find_packages(),
    project_urls={
        'Documentation': 'https://docs.developers.flagship.io/docs/python-v2-1',
        'Source': 'https://github.com/abtasty/flagship-python-sdk'
    },
    install_requires=[
        'requests',
        'typing',
        'six',
        'enum34'
    ]
)
