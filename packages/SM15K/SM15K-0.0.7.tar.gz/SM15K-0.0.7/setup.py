import pathlib
from setuptools import setup

from deltaelektronika import SM15K

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding='utf-8')

# This call to setup() does all the work
setup(
    name="SM15K",
    version="0.0.7",
    description="Delta Elektronika SM15K Power Supply Controller",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/keklikyusuf/DeltaElektronika",
    author="Yusuf Keklik",
    author_email="keklikyusuf@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=[""],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "SMK15=SM15K.__main__:main",
        ]
    },
)