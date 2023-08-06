
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Parneetk-101917044",
    version="1.0.4",
    author="Parneet Kaur Rakhra",
    author_email="prakhra_be19@thapar.edu",
    description="A package that calculates Topsis Score and Rank them accordingly",
    license="MIT",
    url="https://github.com/Parneet-26/Topsis-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["Topsis-Parneetk-101917044"],
    include_package_data=True,
    install_requires='pandas',
)
