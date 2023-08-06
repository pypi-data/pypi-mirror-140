from setuptools import setup, find_packages

setup(
    name='vali_lib',  # mandatory
    version='0.2',  # mandatory
    packages=find_packages(),  # mandatory
    # optional parameters
    description='This is a test project!',
    author='eu',
    author_email='eu@toteu.com',
    url='https://google.com',
    install_requires=['requests==2.24.0', 'pymongo', 'beautifulsoup4'],
    python_requires='>=3.8',
)
