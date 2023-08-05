from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="topsis_shivom_101916036",
    version="0.0.0",
    author="Shivom Chawla",
    author_email="shivomchawla2000@gmail.com",
    description="A small package to work with topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shivom2k/Topsis-Shivom-101916036",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)