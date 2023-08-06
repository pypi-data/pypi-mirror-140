import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Manan-101903311",
    version="1.0.1",
    description="Calculates the Topsis Score and Rank",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Manan Ghai",
    author_email="try@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["Topsis"],
    include_package_data=True,
    install_requires=['numpy','pandas'],
    entry_points={
        "console_scripts": [
            "Topsis=Topsis.__main__:main",
        ]
    },
)
