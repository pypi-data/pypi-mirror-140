import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Sudeep-101903496",
    version="0.0.3",
    author="Sudeep Singh",
    author_email="singhsudeep0202@gmail.com",
    description="A package for calculating Topsis Score and Rank them accordingly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/sudeepk07/Topsis-Sudeep-101903496",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["Topsis_Sudeep_101903496"],
    include_package_data=True,
    install_requires='pandas',
    entry_points={
        "console_scripts": [
            "topsis=Topsis_Sudeep_101903496.topsis:main",
        ]
    },
)
