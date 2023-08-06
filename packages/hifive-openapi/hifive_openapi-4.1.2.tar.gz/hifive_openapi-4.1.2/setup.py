# coding: utf-8
from setuptools import setup, find_packages

version = '4.1.2'

setup(
    name='hifive_openapi',
    version=version,
    description="HIFIVE OpenApi Python SDK",
    long_description="""
openapi_sdk
=======================

HIFIVE OpenApi for Python.

""",
    keywords='hifiveopen_api',
    author='yong.huang',
    author_email='huangyong@hifive.ai',
    url='https://gitlab.ilongyuan.cn/hifive/hifive-openapi-python-sdk',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests >= 2.24.0',

    ],

)
