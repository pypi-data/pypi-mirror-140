from setuptools import setup, find_packages

setup(
    name="aymakan-sdk",
    version="1.1.1",
    description="AyMakan SDK",
    long_description="This is official Aymakan Python SDK. It can be used to integrate with Aymakan APIs.",
    long_description_content_type="text/markdown",
    url="https://github.com/aymakan/python-sdk/",
    author="Aymakan IT",
    author_email="it@aymakan.com.sa",
    license='Apache License 2.0',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=["requests"]
)
