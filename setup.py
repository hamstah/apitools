from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__),"requirements.txt")) as req_file:
    requirements = req_file.read().splitlines()

setup(
    name='apitools',
    version='0.1.2',
    author='Nicolas Esteves',
    author_email='hamstahguru@gmail.com',
    packages=['apitools'],
    url='https://github.com/hamstah/apitools',
    description='Tools to play with json-schema and rest apis',
    long_description=open("README.md").read(),
    install_requires=requirements,
)
