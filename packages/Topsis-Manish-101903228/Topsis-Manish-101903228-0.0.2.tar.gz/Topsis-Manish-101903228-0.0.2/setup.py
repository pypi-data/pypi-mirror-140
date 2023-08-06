
import setuptools 

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent, any Windows,Linux,MacOs,etc",
    ],


setuptools.setup(
    name="Topsis-Manish-101903228",
    version="0.0.2",
    author="Manish Sharma",
    author_email="manish1206s@gmail.com",
    description="A package Calculates Topsis Score and Rank them accordingly, for example selection of best project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="",
    
    packages=["Topsis_Manish_101903228"],
    include_package_data=True,
    install_requires='pandas',
    entry_points={
        "console_scripts": [
            "topsis=Topsis_Manish_101903228.Topsis:main",
        ]
    },
)