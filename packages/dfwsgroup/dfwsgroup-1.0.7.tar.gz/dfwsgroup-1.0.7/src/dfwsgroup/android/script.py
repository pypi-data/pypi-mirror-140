#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/8 13:48
# @Author  : Lifeng
# @Site    : 
# @File    : androidScript.py
# @Software: PyCharm

import os
from loguru import logger
from pathlib import Path
from dfwsgroup.android.handle import Handle

__all__ = ["StabilityTestAndroid"]


class StabilityTestAndroid:
    def __init__(self):
        results = os.popen('adb devices', "r").readlines()
        self._devices = results[1].split("\t")[0]

    def _jar_package_push(self):
        if self._devices:
            logger.info("开始拉取jar包...")
            _path = Path(__file__).parent.joinpath("Fastbot_Android")
            os.system(f"adb push {_path.joinpath('framework.jar')} /sdcard")
            os.system(f"adb push {_path.joinpath('monkeyq.jar')} /sdcard")
            os.system(f"adb push {_path.joinpath('fastbot-thirdpart.jar')} /sdcard")
            logger.info("拉取jar包完成...")
        else:
            raise Exception(f"检查是否连接有问题或adb环境是否正常！")

    def _max_xpath_actions(self):
        if self._devices:
            logger.info("开始push自定义事件序列文件...")
            _path = Path(__file__).parent.parent.joinpath("config")
            os.system(f"adb push {_path.joinpath('max.xpath.actions')} /sdcard")
            logger.info("push自定义事件序列文件完成...")
        else:
            raise Exception(f"检查是否连接有问题或adb环境是否正常！")

    def execute(self, *, packages, minutes: int, throttle: int, is_command):
        if not self._devices:
            raise Exception(f"请检查设备号：{self._devices}")

        self._jar_package_push()
        self._max_xpath_actions()

        logger.info(f"获取参数替换成功的运行命令")
        return Handle(self._devices, packages).command_get(minutes, throttle, is_command)
