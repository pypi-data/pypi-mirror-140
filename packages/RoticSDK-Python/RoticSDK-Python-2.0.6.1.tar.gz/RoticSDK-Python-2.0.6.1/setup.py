import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RoticSDK-Python",
    version="2.0.6.1",
    author="Rotic Intelligent Solutions",
    author_email="dev@rotic.ir",
    description="Python SDK let you call Rotic Intelligent Solutions API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roticmedia/RoticSDK-Python",
    packages=['Rotic','Rotic/Models'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)