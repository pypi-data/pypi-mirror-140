from setuptools import find_packages, setup
from codecs import open
from os import path, getenv


pwd = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(pwd, 'README.MD'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='postmanrenderer',
    packages=find_packages(include=['postmanrenderer']),
    version=getenv("RELEASE_VERSION", "0.1.0"),
    description='Create and Export Postman collections',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Aditya Nagesh',
    author_email="adityagesh@gmail.com",
    license='MIT',
    install_requires=['Jinja2'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.2.5'],
    test_suite='tests',
)
