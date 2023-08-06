# -*- coding: UTF-8 -*-
# @Time : 2021/11/24 上午11:44 
# @Author : 刘洪波
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pygraphdb',
    version='1.1.1',
    packages=setuptools.find_packages(),
    url='https://gitee.com/maxbanana/graphdb',
    license='Apache',
    author='hongbo liu',
    author_email='782027465@qq.com',
    description='A connect graphdb package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
