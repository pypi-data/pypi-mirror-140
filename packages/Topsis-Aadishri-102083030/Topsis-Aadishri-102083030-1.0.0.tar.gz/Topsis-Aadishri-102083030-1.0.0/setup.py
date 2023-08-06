import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Aadishri-102083030",
    version="1.0.0",
    description="Calculates TOPSIS on the given dataset!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/aadishri17/Topsis-Aadishri-102083030",
    author="Aadishri Soni",
    author_email="aadishrisoni123@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["Topsis"],
    include_package_data=True,
    install_requires=['pandas'],
    entry_points={
        "console_scripts": [
            "Topsis=Topsis.__main__:main",
        ]
    },
)