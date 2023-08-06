import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
Readme = (HERE / "Readme.md").read_text()
# This call to setup() does all the work
setup(
    name="Topsis_BhaveshSareen_101917085",
    version="1.0.0",
    description="Assignment of Bhavesh Sareen",
    long_description=Readme,
    long_description_content_type="text/markdown",
    url="",
    author="Bhavesh Sareen",
    author_email="sareenbahvesh26@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["Topsis"],
    include_package_data=True,
    install_requires=[],
)