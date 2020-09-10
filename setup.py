import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='flagship',
    version='12.12.12',
    author="Flagship Team",
    author_email="support@flagship.io",
    description="Flagship Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abtasty/flagship-python-sdk",
    packages=setuptools.find_packages(),
    project_urls={
        'Documentation': 'http://developers.flagship.io/python/v2.0.x/',
        'Source': 'https://github.com/abtasty/flagship-python-sdk'
    },
    install_requires=[
        'requests',
        'typing',
        'six',
        'enum34'
    ]
)
