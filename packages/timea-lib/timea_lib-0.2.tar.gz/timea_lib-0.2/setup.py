from setuptools import setup, find_packages

setup(
    name="timea_lib",  # mandatory
    version="0.2",  # mandatory
    packages=find_packages(),  # mandatory
    # optional parameters
    description="This is  test project!",
    author="Timea",
    author_email="timea@mail.com",
    url="http://google.com",
    install_requires=["requests", "pymongo", "beautifulsoup4"],
    python_requires=">=3.10",
)
