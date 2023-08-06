import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sturl",
    version="0.0.1",
    author="ikenna ogbuanu",
    author_email="ogbuanuikenna66@gmail.com",
    description="A small python framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ogbuanu/sturl",
    project_urls={
        "Bug Tracker": "https://github.com/ogbuanu/sturl/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "sturl"},
    packages=setuptools.find_packages(where="sturl"),
    python_requires=">=3.6",
)