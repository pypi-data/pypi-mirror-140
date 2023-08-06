import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


tests_require = [
    "pytest",
]


setup(
    name="little-pwny",
    version="0.3",
    description="Check whether your password has been pwnd",
    long_description=read("README.rst")
    + "\n\n\n"
    + read("CHANGES.rst")
    + "\n\n\n",
    long_description_content_type="text/x-rst",
    url="https://codeberg.org/ulif/little-pwny",
    author="ulif",
    author_email="uli@gnufix.de",
    license="GPL3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: Utilities",
        "Topic :: Security :: Cryptography",
        (
            "License :: OSI Approved :: "
            "GNU General Public License v3 or later (GPLv3+)"
        ),
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    packages=["pwny"],
    zip_safe=False,
    extras_require={
        "test": tests_require,
    },
    tests_require=tests_require,
    entry_points={"console_scripts": ["pwny = pwny:main"]},
)
