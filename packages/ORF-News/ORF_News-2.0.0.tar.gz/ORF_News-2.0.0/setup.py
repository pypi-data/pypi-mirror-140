import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ORF_News",
    version="2.0.0",
    author="Moritz | mcbabo#6969",
    url="https://github.com/mcbabo/ORF_News_v2",
    description="Simple orf news scraper",
    py_modules=["orf_news"],
    package_dir={"": "orf_news"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "aiohttp >= 3.8",
        "bs4 >= 0.0.1",
        "beautifulsoup4 >= 4.10.0"
    ]
)