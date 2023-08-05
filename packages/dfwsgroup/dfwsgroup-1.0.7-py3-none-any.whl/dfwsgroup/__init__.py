#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/22 11:29
# @Author  : Lifeng
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm

__version__ = "1.0.7"
__description__ = "android-稳定测试，记得配置adb环境."

from dfwsgroup.common.cli import main

__all__ = [
    "__version__",
    "__description__",
    "main"
]
