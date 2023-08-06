import pathlib
from setuptools import setup 
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="topsis-ShreyaGarg-101953015",
    version="1.0.1",
    description="A topsis rank calculator.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/shreyaxgarg/Topsis-Shreya-101953015",
    author="Shreya Garg",
    author_email="sgarg6_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=setuptools.find_packages(),
    install_requires=['pandas'],
)