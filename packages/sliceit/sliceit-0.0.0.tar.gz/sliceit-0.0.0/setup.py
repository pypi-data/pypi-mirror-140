from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="sliceit",
    version="0.0.0",
    description="Dynamically sized slice views which avoid storing their own data.",
    packages=["sliceit"],
    python_requires=">=3.5",
    url="https://github.com/SimpleArt/sliceit",
    author="Jack Nguyen",
    author_email="jackyeenguyen@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license_files=["LICENSE"],
)
