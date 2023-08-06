from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image-processing-pkg-vleite",
    version="0.0.1",
    author="vitor_leite",
    author_email="vitorleite5@outlook.com",
    description="Duplicated project to learn how work packages in Python",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vitoleite/image_processing_dio",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)