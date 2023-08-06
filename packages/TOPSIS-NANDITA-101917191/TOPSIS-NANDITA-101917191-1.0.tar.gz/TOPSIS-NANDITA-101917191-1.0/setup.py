from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name="TOPSIS-NANDITA-101917191",
	version='1.0',
	author='Nandita',
	author_email='nanditabagga23@gmail.com',
	description='topsis package for MCDM problems',
	long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NanditaBagga/TOPSIS-NANDITA-101917191",
    download_url="https://github.com/NanditaBagga/TOPSIS-NANDITA-101917191/archive/refs/tags/1.0.tar.gz",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'topsis=topsis.topsis:main'
        ]
    },
    install_requires=[
        'numpy',
        'pandas',
        'argparse',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)