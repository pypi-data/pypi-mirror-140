import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="topsis_banaj_101916008",
    version="1.0.0",
    author="Banaj Bedi",
    author_email="banaj7@gmail.com",
    description="It's a package that calcuates Topsis score and ranks accordingly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/banajbedi/topsis_banaj_101916008",
    download_url="https://github.com/banajbedi/topsis_banaj_101916008/archive/refs/tags/v1.0.0.tar.gz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["topsis_banaj_101916008"],
    include_package_data=True,
    install_requires='pandas',
    entry_points={
        "console_scripts": [
            "topsis = topsis_banaj_101916008.topsis:main",
        ]
    },
)