import pathlib
from setuptools import setup, find_packages
import sys

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="notipy-py",
    version="1.0.7",
    description="Windows notifier for 9-hours working day using Pomadoro technique "
                "(50 minutes work and 10 minutes rest) with lunch break",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/VladaZakharova/Notifier",
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
        "notifier==1.0.3",
        "plyer==2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "notifier=notifier.__main__:start_notifier",
        ]
    },
)