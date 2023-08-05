import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-naman-101916076",
    version="1.0.2",
    description="TOPSIS method for multiple-criteria decision making (MCDM).",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Naman Kalsotra",
    author_email="Kalsotranaman@gmail.com",
    license="SELF",
    classifiers=[
        
        "Programming Language :: Python :: 3.9",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=["pandas","sys"],
    entry_points={
        "console_scripts": [
            "topsis=topsis.__main__:main",
        ]
    },
)