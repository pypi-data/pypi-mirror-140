import setuptools  # type: ignore


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {"testing": ["nose", "coveralls"]}

setuptools.setup(
    name="mutwo.ext-common-generators",
    version="0.5.1",
    license="GPL",
    description="Common generators extension for event based framework for generative art",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    url="https://github.com/mutwo-org/mutwo.ext-common-generators",
    project_urls={"Documentation": "https://mutwo.readthedocs.io/en/latest/"},
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo.ext-core>=0.54.0, <1.00.0",
        # For the brown, brun and koenig modules
        "numpy>=1.18, <2.00",
        # For the brown module
        "scipy>=1.4.1, <2.0.0",
        # For the koenig module
        "python-ranges>=0.2.0, <1.0.0",
        # For the chomsky module
        "treelib>=1.6.1, <2.0.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
