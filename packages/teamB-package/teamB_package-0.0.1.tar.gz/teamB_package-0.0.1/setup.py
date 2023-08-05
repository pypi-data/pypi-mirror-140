from setuptools import setup
with open("README.md","r") as fh:
    long_description = fh.read()

setup(
    name= 'teamB_package',
    version='0.0.1',
    description='Say hello!',
    py_modules=["demo"],
    package_dir={'':'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
)