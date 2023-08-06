from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        README = f.read()
    return README

setup(
    name="Topsis-Shraddha-101903790",
    version="1.0.0",
    description="The Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS) is a multi-criteria decision analysis method.",
    long_description="README.md",
    long_description_content_type="text/markdown",
    author="svasudeva",
    author_email="svasudeva_be19@thapar.edu",
    license="MIT",
    url="https://github.com/shraddha-debug/Topsis-Shraddha-101903790.git",  
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules = ["topsis"],
    include_package_data=True,
    install_requires=['pandas'],    
)