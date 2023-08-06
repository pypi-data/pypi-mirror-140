import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis_Mayank_102097021",
    version="1.0.0",
    author="Mayank Kumar",
    description="Package to calculate Topsis Score",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["Topsis_Mayank_102097021"],
    include_package_data=True,
    install_requires=['pandas'],
    entry_points={
        "console_scripts": [
            "topsis = Topsis_Mayank_102097021.topsis:main",
        ]
    },
)