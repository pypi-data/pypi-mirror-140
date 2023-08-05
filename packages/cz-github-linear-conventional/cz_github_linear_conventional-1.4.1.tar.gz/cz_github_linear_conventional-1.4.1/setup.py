from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cz_github_linear_conventional",
    version="1.4.1",
    py_modules=["cz_github_linear_conventional"],
    install_requires=["commitizen"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
