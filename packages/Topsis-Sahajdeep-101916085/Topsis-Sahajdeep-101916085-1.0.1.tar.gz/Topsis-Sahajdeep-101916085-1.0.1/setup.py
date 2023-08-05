import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-Sahajdeep-101916085",
    version="1.0.1",
    description="TOPSIS method for multiple-criteria decision making (MCDM).",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Sahajdeep Singh Kharbanda",
    author_email="kharbandasahajsingh@gmail.com",
    license="SELF",
    classifiers=[

        "Programming Language :: Python :: 3.9",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=["pandas","numpy"],
    entry_points={
        "console_scripts": [
            "topsis=topsis._main_:main",
        ]
    },
)
