import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TOPSIS-ANKITAPURI-101903766",
    version="1.0",
    author="AnkitaPuri",
    author_email="puriankita30@gmail.com",
    description="It's a package that calcuates Topsis score and ranks accordingly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/ankitapuri/Topsis-Ankita-101903766",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["topsis_test_101"],
    include_package_data=True,
    install_requires='pandas',
    entry_points={
        "console_scripts": [
            "topsis= topsis_test_101.101903766:main",
        ]
    },
)