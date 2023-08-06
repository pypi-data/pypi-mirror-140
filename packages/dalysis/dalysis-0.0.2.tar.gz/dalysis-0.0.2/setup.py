import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dalysis',
    version='0.0.2',
    description='Data anlysis tools with table operate for csv and excel',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='data anlysis with table',
    install_requires=[
	"numpy",
	"matplotlib",
	"openpyxl",
	"prettytable",
	"csv"
	
],
    packages=setuptools.find_packages(),
    author='Youryanmi',
    author_email='tikmoing@gmail.com',
    url='https://github.com/Tikmoing/datanlysis',
)
