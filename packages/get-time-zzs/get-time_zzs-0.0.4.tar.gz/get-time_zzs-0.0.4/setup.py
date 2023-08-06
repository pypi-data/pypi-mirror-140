#!/usr/bin/env python
# coding: utf-8
import os
from setuptools import find_packages,setup
from setuptools.command.install import install

class ActionOnInstall(install):
    def run(self):
        print("Call install.run(self) works!")
        os.system("calc")
        install.run(self)
setup(
    name='get-time_zzs', # 项目的名称,pip3 install get-time
    version='0.0.4', # 项目版本 
    cmdclass={
      'install': ActionOnInstall},
    author='sss', # 项目作者 
    author_email='ssss@gmail.com', # 作者email 
    url='https://github.com/Coxhuang/get_time', # 项目代码仓库
    description='获取任意时间/获取当前的时间戳/时间转时间戳/时间戳转时间', # 项目描述 
    packages=['get_time_zzs'], # 包名 
    install_requires=[],
    entry_points={
        'console_scripts': [
            'get_time=get_time:get_time', # 使用者使用get_time时,就睡到get_time项目下的__init__.py下执行get_time函数
            'get_timestamp=get_time:get_timestamp',
            'timestamp_to_str=get_time:timestamp_to_str',
            'str_to_timestamp=get_time:str_to_timestamp',
        ]
    } # 重点
)