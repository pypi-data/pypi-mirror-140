import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Paras-401903027",
    version="1.0.1",
    author="Paras Tandon",
    author_email="ptandon_bemba19@thapar.edu",
    description="Executes TOPSIS function on csv type files",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["dist"],
    include_package_data=True,
    install_requires=[]
)
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()