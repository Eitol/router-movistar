"""
Setup
"""
import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="router_movistar",
    version="1.0.0",
    description="A package to extract information from Movistar routers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Eitol/router-movistar",
    author="Hector Oliveros",
    author_email="hector.oliveros.leon@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["plantuml_creator"],
    include_package_data=True,
    install_requires=[
        "requests~=2.31.0",
        "pydantic~=2.7.1",
    ],
    entry_points={
        "console_scripts": []
    },
)
