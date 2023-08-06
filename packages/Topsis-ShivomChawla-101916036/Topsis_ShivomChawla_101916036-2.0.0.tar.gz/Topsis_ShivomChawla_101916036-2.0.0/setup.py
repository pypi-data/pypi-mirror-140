from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Topsis_ShivomChawla_101916036",
    version="2.0.0",
    author="Shivom",
    author_email="schawla_be19@thapar.edu",
    description="A small package to work with topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shivom2k/Topsis_ShivomChawla_101916036",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)