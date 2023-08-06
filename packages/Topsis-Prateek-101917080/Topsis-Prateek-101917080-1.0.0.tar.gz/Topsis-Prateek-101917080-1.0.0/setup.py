import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
Readme = (HERE / "Readme.md").read_text()
# This call to setup() does all the work
setup(
    name="Topsis-Prateek-101917080",
    version="1.0.0",
    description="Assignment of Prateek Bansal",
    long_description=Readme,
    long_description_content_type="text/markdown",
    url="",
    author="Prateek Bansal",
    author_email="prateekbansal64@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=[],
)