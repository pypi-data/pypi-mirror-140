from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'Tavishi_101903046',
    version="4.1.1",
    author = 'The Enchanted Carrot',                   
    author_email = 'tsharma1_be19@thapar.edu',
    description="Topsis score rank generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tavishi18/101903046",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)