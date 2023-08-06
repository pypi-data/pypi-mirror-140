import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Gitesh-101903031",
    version="0.0.2",
    author="Gitesh Garg",
    author_email="giteshgarg2002a@gmail.com",
    description="This package is for topsis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['Topsis-Gitesh-101903031'],
    include_package_data = True,
    python_requires=">=3.6",
)