import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bengalianalyzer",
    license="GNU General Public License v3.0",
    version="0.0.102",
    author="A. A. Noman Ansary",
    author_email="showrav.ansary.bd@gmail.com",
    description="A package for analyzing entities present in Bengali sentence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/showrav-ansary/bengali_analyzer",
    project_urls={
        "Bug Tracker": "https://github.com/showrav-ansary/bengali_analyzer/issues",
    },
    install_requires=['pandas', 'indicparser'],
    include_package_data=True,
    package_data={'': ['src/bengali_analyzer/assets/*.csv', 'src/bengali_analyzer/assets/*.txt']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    zip_safe=False,
)
