from setuptools import setup,find_packages

setup(
    name = "marius_lib",#mandatory
    version = "0.1",#mandatory
    packages=find_packages(),#mandatory

#optional parameters
    description = "This is a test project",
    author="eu",
    author_email="eu@toteu.com",
    url="https://google.com",
    install_requires=["requests","pymongo","beautifulsoup4"],
    python_requires=">=3.10"
)