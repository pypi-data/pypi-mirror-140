import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uuidentifier",
    version="0.0.5",  # Latest version .
    author="slipper",
    author_email="r2fscg@gmail.com",
    description="Universally Unique Identifier package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/private_repo/uuidentifier",
    packages=setuptools.find_packages(),
    install_requires=[
        'joblib'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
