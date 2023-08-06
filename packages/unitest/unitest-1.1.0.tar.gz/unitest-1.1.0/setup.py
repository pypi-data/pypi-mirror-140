import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unitest",
    version="1.1.0",
    author="Zeta",
    description="Utilities required for performance and functional tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["selenium>=4.1.0",
                       "gevent>=21.8.0",
                       "geventhttpclient>=1.5.3",
                        "psycogreen>=1.0.2",
                        "locust>=2.6.0",
                        "requests>=2.26.0",
                        "jsonpath-ng>=1.5.3",
                        "greenlet==1.1.2",
                        "psycopg2-binary>=2.9.2"]


)
