from setuptools import setup, find_packages

VERSION = "1.3"
DESCRIPTION = "Downloader for NPTEL"
LONG_DESC = open("./README.md", "r").read()
URL = "https://github.com/deshdeepak1/nptel-dl"
AUTHOR = "Deshdeepak"
AUTHOR_EMAIL = "rkdeshdeepak1@gmail.com"
KEYWORDS = "nptel NPTEL dl download downloader"
LICENSE = "MIT"
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
setup(
    name="nptel-dl",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(),
    py_modules=["nptel_dl"],
    entry_points={"console_scripts": ["nptel-dl=nptel_dl:main"]},
    install_requires=["bs4", "requests", "gdown", "yt-dlp"],
    zip_safe=True,
)
