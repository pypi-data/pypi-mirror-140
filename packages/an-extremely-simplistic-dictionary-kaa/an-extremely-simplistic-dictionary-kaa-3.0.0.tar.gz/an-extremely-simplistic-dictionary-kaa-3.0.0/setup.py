from setuptools import setup

setup(
    # TODO: Write a globally unique name which will be listed on PyPI
    name="an-extremely-simplistic-dictionary-kaa",
    author="Kaan Atakan Aray",  # TODO: Write your name
    version="3.0.0",
    packages=["dictionary"],
    install_requires=[
        "requests>=2.23.0",
    ],
    python_requires=">=3.8",

)
