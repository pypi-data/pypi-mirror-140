import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Prateek-101916078",
    version="1.0.2",
    description="Topsis in python that take input csv file and outputs csv file",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/prateek11rai/Topsis-Prateek-101916078",
    author="Prateek Rai",
    author_email="prateek11rai@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=["pandas"],
    entry_points={
        "console_scripts": [
            "topsis=topsis.__main__:main",
        ]
    },
)