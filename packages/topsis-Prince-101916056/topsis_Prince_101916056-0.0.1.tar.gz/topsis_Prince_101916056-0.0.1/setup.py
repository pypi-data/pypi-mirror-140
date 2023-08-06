from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="topsis_Prince_101916056",
    version="0.0.1",
    author="Prince Saini",
    author_email="pprince_be19@thapar.edu",
    description="A small package to work with topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Prince-hash-lab/topsis_Prince_101916056",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)