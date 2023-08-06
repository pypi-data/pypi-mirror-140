import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DHPyUtilPack",
    version="0.0.1.2",
    author="DongHoon Kim",
    author_email="donghoon5793@gmail.com",
    description="Personal Python Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DongHoon5793/DH_PyPackage",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
