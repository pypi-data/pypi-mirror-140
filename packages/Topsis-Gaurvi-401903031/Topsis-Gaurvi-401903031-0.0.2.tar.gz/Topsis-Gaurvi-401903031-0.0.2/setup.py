import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="Topsis-Gaurvi-401903031",
    version="0.0.2",
    description="The package calculates the topsis score and respective rank",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Gaurvi Rajwanshi",
    author_email="gaurvi966@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    install_requires=['numpy', 'pandas'],
    entry_points={
        "console_scripts": [
            "topsis=topsis.__main__:main",
        ]
    },
)
