import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cnnutilstp",
    version="3.0.0",
    author="tragadoss",
    author_email="heitam159@gmail.com",
    description="file needed in the tp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tragadoss/cnnutils",
    project_urls={
        "Bug Tracker": "https://github.com/Tragadoss/cnnutils",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)