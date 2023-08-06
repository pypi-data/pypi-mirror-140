import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Yash-101903036",
    version="0.0.3",
    author="Yash Upadhyay",
    author_email="yupadhyay_be19@thapar.edu",
    description="A package for topsis score and rank calculations",
    long_description='A package for topsis score and rank calculations',
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["Topsis-Yash-101903036"],
    include_package_data=True,
    # package_dir={"": "Topsis-Yash-101903036"},
    # packages=setuptools.find_packages(where='Topsis-Yash-101903036'),
    python_requires=">=3.6",
)