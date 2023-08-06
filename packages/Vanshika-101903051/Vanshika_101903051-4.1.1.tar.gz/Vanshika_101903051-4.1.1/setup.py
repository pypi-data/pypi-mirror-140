from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'Vanshika_101903051',
    version="4.1.1",
    author = 'Vanshika Mahajan',
    author_email = 'vmahajan1_be19@thapar.edu',
    description="Topsis score and rank generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vm14082001/Vanshika_101903051",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)