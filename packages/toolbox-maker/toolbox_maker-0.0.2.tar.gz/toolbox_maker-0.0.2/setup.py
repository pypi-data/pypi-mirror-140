# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("./README.md", "r") as read_me_file:
    long_desc = read_me_file.read()

setup(
    name='toolbox_maker',
    version='0.0.2',
    url='https://git.srv.bergenkom.no/rp376/Toolbox-Maker',
    license='MIT LICENSE',
    author='Magnus Eikemo Larsen',
    author_email='magnus.larsen@bergen.kommune.no',
    description='This small python program was made for easier use of Python Toolboxes (.pyt) in IDEs The advantage '
                'is that you can write the Toolbox in pure python and the program can convert the python-script '
                'to a real Python Tool.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    include_package_data=True,
    py_modules=["toolbox_maker"],
    keywords=['Python', 'ArcGIS Pro', 'ArcGIS', 'GP', 'GP Tools', 'Tool', 'Tools', 'Python3'],
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[]
)
