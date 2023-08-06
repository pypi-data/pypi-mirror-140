from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="sphinxcontrib-apa",               # This is the name of the package
    version="1.0.0",                        # The initial release version
    author="Jean M. Lescure",               # Full name of the author
    license="Apache-2.0",                          # The license
    description="Simple APA citation style for Sphinx and Jupyter Book",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    install_requires=[],                    # Install other dependencies if any
    packages=find_packages(),               # List of all python modules to be installed
    namespace_packages=["sphinxcontrib"],   # Directory of the source code of the package
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
)
