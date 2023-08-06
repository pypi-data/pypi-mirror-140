from setuptools import setup, find_packages
from datetime import datetime

now = datetime.now()
date_time = now.strftime("%Y%m%d%H%M%S")
version_number = "0.0." + date_time

with open("version_info.txt", "w") as f:
    f.write(version_number)

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["pandas==1.4.1"]

setup(
    name="stockeasy",
    version=version_number,
    author="Adam Blacke",
    author_email="adamblacke@gmail.com",
    description="A package for a quick and dirty portfolio analysis.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/AdamBlacke/stockeasy",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
