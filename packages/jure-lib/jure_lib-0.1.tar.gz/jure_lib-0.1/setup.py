from setuptools import setup, find_packages

setup(
    name='jure_lib',  # madatory
    version='0.1',  # madatory
    packages=find_packages(),  # madatory
    # optional parameters
    description='This is a test project!',
    author='eu',
    author_email='eu@toteu.com',
    url='https://google.com',
    install_requires=['requests==2.24.0', 'pymongo', 'beautifulsoup4'],
    python_requires='>=3.10',
)