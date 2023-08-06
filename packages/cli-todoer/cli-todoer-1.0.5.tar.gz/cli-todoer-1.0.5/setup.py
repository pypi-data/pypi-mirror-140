import pathlib
from setuptools import setup, find_packages
import sys

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="cli-todoer",
    version="1.0.5",
    description="An easy command line interface for saving tasks to to-do list for current day",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/VladaZakharova/CLI-todoer",
    author="Vlada Zakharova",
    author_email="vladazaharova0@gmail.com",
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("venv", ".git",)),
    include_package_data=True,
    install_requires=[
        "typer==0.4.0",
        "rich==11.0.0",
        "click==8.0.3",
        "commonmark==0.9.1",
        "typing-extensions==4.1.1"
    ] + (["colorama==0.4.4"] if "win" in sys.platform else []),
    entry_points={
        "console_scripts": [
            "todoer1=todoer.todocli:main",
        ]
    },
)