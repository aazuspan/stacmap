from setuptools import setup

version = "0.0.4"

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

requirements = ["pystac", "folium", "numpy", "branca"]
doc_requirements = ["nbsphinx", "sphinx", "sphinx_rtd_theme"]
test_requirements = ["pytest", "coverage", "matplotlib"]
dev_requirements = (
    [
        "pre-commit",
        "mypy",
        "black",
        "isort",
        "bumpversion",
        "twine",
    ]
    + doc_requirements
    + test_requirements
)

extras_require = {
    "doc": doc_requirements,
    "dev": dev_requirements,
    "test": test_requirements,
}

setup(
    name="stacmap",
    author="Aaron Zuspan",
    author_email="aazuspan@gmail.com",
    url="https://github.com/aazuspan/stacmap",
    version=version,
    description="Create interactive maps of STAC items.",
    long_description=readme + "\n\n",
    long_description_content_type="text/markdown",
    keywords="STAC,folium,map,interactive,cloud-native-geospatial",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: GIS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
    ],
    license_files=("LICENSE",),
    license="MIT",
    packages=["stacmap"],
    test_suite="tests",
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require=extras_require,
    python_requires=">=3.7",
)
