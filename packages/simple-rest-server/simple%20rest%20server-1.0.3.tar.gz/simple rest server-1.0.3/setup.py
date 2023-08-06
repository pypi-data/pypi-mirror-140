import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='simple rest server',
    version='1.0.3',
    author="Pavel Lavi",
    author_email="LaviPavel@outlook.com",
    description="simple rest server based on flask, useful for rest rest integration testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pavel_lavi/simple-rest-server",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    platforms='any',
    python_requires='>=3.6',
    setup_requires=["pytest-runner"],
    install_requirements=["Flask>=2.0.3"],
    tests_requirements=["pytest"],
)
