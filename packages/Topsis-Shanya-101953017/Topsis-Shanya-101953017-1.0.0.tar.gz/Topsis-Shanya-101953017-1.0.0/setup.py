import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Shanya-101953017",
    version="1.0.0",
    description="It performs topsis for any model",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Shanya1356/Topsis-Shanya-101953017",
    author="Shanya",
    author_email="sbibhuty_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "Topsis=Topsis._main_:main",
        ]
    },

)