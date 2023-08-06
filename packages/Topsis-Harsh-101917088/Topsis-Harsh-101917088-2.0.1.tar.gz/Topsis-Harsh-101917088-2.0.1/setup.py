from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

DESCRIPTION = 'Topsis Feature Choosing System'
LONG_DESCRIPTION = 'A package that allows to operate on a given csv file and run data accordingly'

# Setting up
setup(
    name="Topsis-Harsh-101917088",
    author="Harsh Kashyap",
    version="2.0.1",
    author_email="hkashyap_be19@thapar.edu",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'sys','math', 'copy'],
    keywords=['python', 'TOPSIS', 'Ranking'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
