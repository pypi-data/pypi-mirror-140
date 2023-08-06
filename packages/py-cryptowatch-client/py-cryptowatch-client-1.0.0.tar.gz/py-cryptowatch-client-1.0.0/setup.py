import pathlib

from setuptools import setup

ROOT = pathlib.Path(__file__).parent

README = (ROOT / "README.md").read_text()

setup(
    name="py-cryptowatch-client",
    version="1.0.0",
    description="Cryptowatch API wrapper",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/nlnsaoadc/py-cryptowatch",
    author="nlnsaoadc",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["cryptowatch"],
    include_package_data=True,
    install_requires=["requests"],
)
