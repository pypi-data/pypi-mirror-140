from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Topsis package'

# Setting up
setup(
    name="topsis_101903681",
    version=VERSION,
    author="Hemant Garg",
    author_email="<hgarg5_be19@thapar.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['sys','pandas','numpy','scipy','os'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)