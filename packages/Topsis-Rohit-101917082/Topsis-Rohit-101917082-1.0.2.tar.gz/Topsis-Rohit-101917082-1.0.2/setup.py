import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Rohit-101917082",
    version="1.0.2",
    description="It calculates topsis score of the data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Rohit-singla-2310/Topsis-Rohit-101917082",
    author="Rohit Singla",
    author_email="rsingla_be19@thapar.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    py_modules=["Topsis-Rohit-101917082"],
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[],
    # entry_points={
    #     "console_scripts": [
    #         "square=square.__main__:main",
    #     ]
    # },
)