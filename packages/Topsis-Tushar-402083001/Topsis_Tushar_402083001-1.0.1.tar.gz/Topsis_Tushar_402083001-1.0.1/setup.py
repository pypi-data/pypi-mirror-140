from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name = "Topsis_Tushar_402083001",
    version = "1.0.1",
    description = "A Python package for implementing TOPSIS",
    long_description = readme(),
    long_description_content_type = "text/markdown",
    author = "Tushar Verma",
    author_email = "tusharverma643@gmail.com",
    license = "MIT",
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["Topsis_Tushar_402083001"],
    include_package_data = True,
    install_requires = ["pandas"],
)