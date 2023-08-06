#coding:utf-8

from os import path
from codecs import open
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="oss-client",
    version="0.1.4",
    author="olivetree",
    license="MIT",
    packages=["oss_client"],
    author_email="olivetree123@163.com",
    url="https://github.com/olivetree123/oss-client",
    description="OSS Client for AliyunOSS/TencentOSS/QiniuOSS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "requests>=2.18.0",
        "oss2==2.15.0",
        "qiniu==7.5.0",
        "cos-python-sdk-v5==1.9.10",
    ],
)
