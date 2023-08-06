from setuptools import setup, find_packages

setup(
    # mandatory parameters
    name="Cip_library",
    version="0.2",
    packages=find_packages(),
    # optional parameters
    description="This is a test project",
    author="Cip",
    author_email="Cip@gmail.com",
    url="https://cip_library.com",
    install_requires=["request", "pandas"],
    python_requires=">=3.10"
)
