import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pysharkfeat",
    version="0.1",
    author="Zhi Liu",
    author_email="cowliucd@gmail.com",
    description="an open source TLS encrypted traffic feature extraction tool from pcaps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zliucd/pysharkfeat",
    packages=setuptools.find_packages(),
    install_requires=['numpy>=1.18'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)