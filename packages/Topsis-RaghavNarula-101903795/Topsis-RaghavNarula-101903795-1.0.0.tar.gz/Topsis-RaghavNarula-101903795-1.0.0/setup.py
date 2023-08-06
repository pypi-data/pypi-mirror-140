import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="Topsis-RaghavNarula-101903795",
    version="1.0.0",
    description="It gives a csv file that includes the topsis result",
    long_description=README,
    long_description_content_type="text/markdown",
    
    author="Raghav Narula",
    author_email="rnarula_be19@thapar.edu",
    license="MIT",
    classifiers=[
        #"License :: OSI Apved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["topsis"],
    include_package_data=True,
    install_requires=['pandas','numpy'],
    setup_requires=['wheel'],
    entry_points={
        "console_scripts": [
            "topsis=topsis.topsis:get_topsis_result",
        ]
    },
)

# The directory containing this file


# This call to setup() does all the work
