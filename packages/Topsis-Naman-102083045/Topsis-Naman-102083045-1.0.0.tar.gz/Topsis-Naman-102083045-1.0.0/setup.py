import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Naman-102083045",
    version="1.0.0",
    description="Topsis",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    author="Naman Garg",
    author_email="ngarg4_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["topsisNaman"],
    include_package_data=True,
    install_requires=[],
)