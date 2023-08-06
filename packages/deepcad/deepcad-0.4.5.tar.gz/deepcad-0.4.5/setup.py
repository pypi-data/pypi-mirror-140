# -*- coding: utf-8 -*-
#############################################
# File Name: setup.py
# Author: Yixin Li
# Mail: 20185414@stu.neu.edu.cn
# Created Time:  2021-12-11
#############################################
from setuptools import setup, find_packages



with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()


setup(
    name="deepcad",
    version="0.4.5",
    description=("implemenent DeepCAD to denoise data by "
                 "removing independent noise"),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Xinyang Li, Yixin Li",
    author_email="20185414@stu.neu.edu.cn",
    url="https://github.com/cabooster/DeepCAD-RT",
    license=license,
    packages=find_packages(),
    install_requires=['matplotlib','pyyaml','tifffile','scikit-image','opencv-python','csbdeep','gdown==4.2.0'],
)
