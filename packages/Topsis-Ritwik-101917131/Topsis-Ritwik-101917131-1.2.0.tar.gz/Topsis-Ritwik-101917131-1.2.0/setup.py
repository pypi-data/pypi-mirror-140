import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Topsis-Ritwik-101917131",
    packages=["Topsis-Ritwik-101917131"],
    version="1.2.0",
    author="Ritwik Khanna",
    author_email="khannaritwik.rk@gmail.com",
    description="Package to calculate Topsis Score and Rank them accordingly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=['Python', 'Topsis', 'UCS654'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        
    ],
    include_package_data=True,
    install_requires='pandas',
)
