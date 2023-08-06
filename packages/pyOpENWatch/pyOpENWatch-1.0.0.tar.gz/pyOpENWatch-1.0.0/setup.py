import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pyOpENWatch",
    version="1.0.0",
    description="Track NFTs as they are minted in the blockchain ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ArtShield/pyOpENWatch",
    author="Ege Emir Ozkan",
    author_email="egeemirozkan24@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["pyopenwatch"],
    include_package_data=True,
    install_requires=["requests"],
)
