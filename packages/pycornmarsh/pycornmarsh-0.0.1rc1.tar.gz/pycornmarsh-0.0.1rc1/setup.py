from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


extras_require = {
    "test": [
        "pytest",
        "pytest-cov",
        "webtest",
        "tox",
    ],
    "ci": [
        "python-coveralls",
    ],
}

extras_require.update(
    {
        "dev": extras_require["test"]
        + [
            "black",
        ]
    }
)


setup(
    name="pycornmarsh",
    version="0.0.1-rc1",
    description="Automated OpenAPI documentation with Pyramid Cornice and Marshmallow ",
    long_description=long_description,
    license="BSD",
    long_description_content_type="text/markdown",
    url="https://github.com/debonzi/pycornmarsh",
    author="Daniel Debonzi",
    author_email="debonzi@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="pyramid openapi apispec marshmallow cornice rest restful",
    packages=find_packages(
        exclude=[
            "tests",
        ]
    ),
    package_data={},
    install_requires=[
        "pyramid-apispec>=0.4",
        "cornice>=6.0.0",
        "marshmallow>=3.13.0,<4.0.0",
        "marshmallow-oneofschema>=3.0.1,<4.0.0",
    ],
    setup_requires=[],
    extras_require=extras_require,
)
