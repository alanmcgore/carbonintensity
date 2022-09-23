"""Setup configuration."""
from setuptools import setup, find_packages

dependencies = ["aiohttp", "numpy"]
test_dependencies = ["pytest", "pytest-asyncio"] + dependencies


with open("README.md", "r") as fh:
    README = fh.read()
setup(
    name="carbonintensity-forked",
    version="0.4.0",
    author="Original work by Jorge Cruz-Lambert with additions by Jean-François Paris & Alan Gore",
    author_email="alanmcgore@gmail.com",
    description="Home Assistant Client library for Carbon Intensity API - Adds work by jfparis and alanmcgore to expose additional forecasts and percentage renewables",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/alanmcgore/carbonintensity",
    packages=find_packages(),
    install_requires=dependencies,
    setup_requires=["pytest-runner"],
    tests_require=test_dependencies,
    extras_require={"test": test_dependencies},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
