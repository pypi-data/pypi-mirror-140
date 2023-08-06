import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rawproxy",
    version="0.0.1",
    author="Devecor",
    author_email="devecor@outlook.com",
    description="a githubusercontent proxy tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DevecorSoft/rawproxy",
    project_urls={
        "rawproxy": "https://github.com/DevecorSoft/rawproxy",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    install_requires=[
        "flask>=2.0.2",
        "gunicorn>=20.1.0",
        "requests>=2.27.1"
    ],
    python_requires=">=3.6",
)