import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='simple rest server',
	version='1.0',
	author="Pavel Lavi",
	author_email="LaviPavel@outlook.com",
	description="simple rest server based on flask, useful for rest rest integration testing",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://gitlab.com/pavel_lavi/simple-rest-server",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	license='MIT',
	platforms='any',
	python_requires='>=2.7'
)
