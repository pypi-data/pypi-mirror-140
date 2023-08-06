import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [requirement for requirement in open('requirements.txt')]

setuptools.setup(
    name="RanCE",                     # This is the name of the package
    version="0.0.2",                        # The initial release version
    author="Featureprenuer",                     # Full name of the author
    description="Random Code Emitter",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=["RanCE", "RanCE.*"]),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["RanCE"],             # Name of the python package
    # package_dir={'':'cricpy2/src'},# Directory of the source code of the package
    install_requires=requirements,
    include_package_data=True                # Install other dependencies if any
)