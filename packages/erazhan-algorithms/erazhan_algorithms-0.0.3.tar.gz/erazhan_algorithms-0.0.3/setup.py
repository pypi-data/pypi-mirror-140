# -*- coding = utf-8 -*-
# @time: 2022/2/18 5:52 下午
# @Author: erazhan
# @File: setup.py

# ----------------------------------------------------------------------------------------------------------------------
from setuptools import setup, find_packages

setup(
    name = "erazhan_algorithms",
    version = "0.0.3",  # 暂时在__init__.py文件中自定义__version__
    
    keywords = ("erazhan_algorithms"),
    description = "algorithm model",
    long_description = "common algotithm usage",
    license = "MIT Licence",

    url = "https://github.com/erazhan/erazhan_algorithms",
    author = "erazhan",
    author_email = "erazhan@163.com",

    python_requires='>=3.6.1',  # 不需要太高的版本
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["torch","transformers","erazhan_utils"]  # ["torch==1.7.0","transformers==4.5.1",]
)