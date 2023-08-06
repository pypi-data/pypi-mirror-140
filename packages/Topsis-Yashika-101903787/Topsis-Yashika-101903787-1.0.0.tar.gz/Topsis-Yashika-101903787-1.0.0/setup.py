from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.0'
DESCRIPTION = 'Calculates Topsis Score and Rank'
LONG_DESCRIPTION = 'It calculates the Topsis Score and rank according to the score of the given input data'

# Setting up
setup(
    name="Topsis-Yashika-101903787",
    version=VERSION,
    author="Yashika Gupta",
    author_email="ms.yashikagupta@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy', 'pandas']
)
# import pathlib
# from setuptools import setup
#
# HERE = pathlib.Path(__file__).parent
#
# README = (HERE / "README.md").read_text()
#
# setup(
#     name="Topsis-Yashika-101903787",
#     version="1.0.0",
#     description="Calculates the topsis score and respective rank",
#     long_description=README,
#     long_description_content_type="text/markdown",
#     author="Yashika Gupta",
#     author_email="ms.yashikagupta@gmail.com",
#     packages=["topsis"],
#     include_package_data=True,
#     install_requires=['numpy', 'pandas'],
#     entry_points={
#         "console_scripts": [
#             "topsis=topsis.__main__:main",
#         ]
#     },
# )
