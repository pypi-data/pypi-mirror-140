import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Kuber-101917160",
    version="0.0.2",
    author="Kuber Mehra",
    author_email="kubermehra2000@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        #"License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "Topsis-Kuber-101917160"},
    packages=setuptools.find_packages(where="Topsis-Kuber-101917160"),
    python_requires=">=3.6",
)