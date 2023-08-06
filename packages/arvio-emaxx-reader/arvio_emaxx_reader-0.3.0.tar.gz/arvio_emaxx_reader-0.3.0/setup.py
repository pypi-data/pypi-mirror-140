import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="arvio_emaxx_reader",
    version="0.3.0",
    author="Jamie Penney",
    description="A library to read from an Arvio Emaxx on the local network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamiepenney/arvio_emaxx_reader",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests_async >= 0.6.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
