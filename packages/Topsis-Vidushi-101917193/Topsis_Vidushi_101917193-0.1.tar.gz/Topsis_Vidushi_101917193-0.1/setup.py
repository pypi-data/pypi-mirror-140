import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	# Here is the module name.
	name="Topsis_Vidushi_101917193",

	# version of the module
	version="0.1",

	# Name of Author
	author="Vidushi Goyal",

	# your Email address
	author_email="goyalvidushi2@gmail.com",

	# #Small Description about module
	description='A python package to implement topsis',
	long_description_content_type="text/markdown",
	# url="https://github.com/username/",
    #download_url = "https://github.com/vidushi2001/Topsis/archive/refs/tags/0.1.tar.gz"
	packages=setuptools.find_packages(),

	 install_requires=[
        'numpy',
        'pandas',
    ],
 	keywords=['topsis', 'Rank', 'Best', 'Model'],

	license="MIT",

	# classifiers like program is suitable for python3, just leave as it is.
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)