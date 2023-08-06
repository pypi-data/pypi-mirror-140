import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="gameday-guru-sdk",
    version="0.0.0",
    description="The Gameday Guru SDK",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/realpython/reader",
    author="Real Python",
    author_email="info@realpython.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["gsdk"],
    include_package_data=True,
    install_requires=[
        "numpy==1.22.2",
        "Pillow==9.0.1",
        "PyJWT==2.3.0",
        "python-dotenv==0.19.2",
        "torch==1.10.2",
        "torchaudio==0.10.2",
        "torchvision==0.11.3",
        "types-cryptography==3.3.15",
        "types-enum34==1.1.8",
        "types-ipaddress==1.0.8",
        "types-PyJWT==1.7.1",
        "typing_extensions==4.1.1"
    ],
    entry_points={
        "console_scripts": [
            "realpython=reader.__main__:main",
        ]
    },
)