#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/11 09:24
# @Author  : Lifeng
# @Site    : 
# @File    : setup.py
# @Software: PyCharm

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fastrun",
    description="快速启动-android稳定性测试",

    version="1.0.3",
    author="liFeng",
    author_email="960158047@qq.com",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://gitee.com/dongfang_rising_test/test-tool.git",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    requires=["Jinja2", "pyyaml", "loguru"],
    package_data={
        "": ["*.txt"],
        "dfwsgroup": ["data/*.json", "config/*", "android/Fastbot_Android/*.jar"],
    }
)
