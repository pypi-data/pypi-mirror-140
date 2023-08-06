import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="typetwo",
    version="1.0.22",
    author="Mark White",
    author_email="maranite@gmail.com",
    description="Helper for type-II Slowly Changing Dimensions, as well as ISO Json loading and dumping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maranite/typetwo",
    project_urls={
        "Bug Tracker": "https://github.com/maranite/typetwo/issues",
        "About Mark" : "https://www.linkedin.com/in/maranite/"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    test_suite='nose.collector',
    tests_require=['nose'], 
)