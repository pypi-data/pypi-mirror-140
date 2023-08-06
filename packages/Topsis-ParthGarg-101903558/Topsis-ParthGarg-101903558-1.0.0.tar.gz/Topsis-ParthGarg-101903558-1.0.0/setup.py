import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-ParthGarg-101903558",
    version="1.0.0",
    description="It gives a csv file.",
    long_description=README,
    long_description_content_type="text/markdown",
    
    author="Parth Garg",
    author_email="parthgarg2013@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=['pandas','numpy'],
    setup_requires=['wheel'],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:get_topsis_result",
        ]
    },
)