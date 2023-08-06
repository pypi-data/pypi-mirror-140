from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'python_topsis_Samridhi_101916086',
    version="4.3.1",
    author = 'Samridhi',                   
    author_email = 'sgarg7_be19@thapar.edu',
    description="Topsis score and rank generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Samridhi412/python_topsis_Samridhi_101916086",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)