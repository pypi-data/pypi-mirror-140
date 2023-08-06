from setuptools import find_packages, setup

setup(
    name="molplotly",
    version="1.0.1",
    description="plotly add-on to render molecule images on mouseover",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wjm41/molplotly",
    author="William McCorkindale",
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=[
        "dash",
        "plotly",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
)
