import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

PROJECT_NAME = "aiFlow_pypi"
USERNAME = "Hassi34"


setuptools.setup(
    name=f"{PROJECT_NAME}-{USERNAME}",
    version="0.0.1",
    author= USERNAME,
    author_email="hasnainmehmood3435@gmail.com",
    description="It's an Implimentation of Perceptron",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{USERNAME}/{PROJECT_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{USERNAME}/{PROJECT_NAME}/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires = [
        "numpy",
        "tqdm"
    ]
)   