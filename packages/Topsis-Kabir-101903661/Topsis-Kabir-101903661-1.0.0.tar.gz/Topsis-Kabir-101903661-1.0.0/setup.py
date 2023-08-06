import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Kabir-101903661",
    version="1.0.0",
    description="Topsis analysis for a dataframe",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sethkabir/Topsis-Kabir-101903661",
    author="Kabir Seth",
    author_email="seth.kabir14@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["Topsis-Kabir-101903661"],
    include_package_data=True,
    install_requires=[],
)
