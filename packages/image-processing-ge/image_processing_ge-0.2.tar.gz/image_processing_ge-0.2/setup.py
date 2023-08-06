from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_ge",
    version="0.2",
    author="Gustavo Ellwanger",
    author_email="gustavojce@gmail.com",
    description="Projeto para o Bootcamp Cognizant Cloud Data Engineer #2",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gellwanger",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
