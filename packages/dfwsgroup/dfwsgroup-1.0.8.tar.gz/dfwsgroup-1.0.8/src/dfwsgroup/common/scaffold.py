#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/18 21:04
# @Author  : Lifeng
# @Site    : 
# @File    : scaffold.py
# @Software: PyCharm

import os
import sys
import time
import logging


def init_parser_scaffold(subparsers):
    sub_parser_scaffold = subparsers.add_parser(
        "startproject", help="创建一个模板工程目录。"
    )
    sub_parser_scaffold.add_argument(
        "project_name", type=str, nargs="?", help="指定项目名称。"
    )
    return sub_parser_scaffold


def create_scaffold(project_name):
    def create_folder(path):
        try:
            os.makedirs(path)
            logging.info(f"创建文件夹：{path}")
            return 0
        except Exception as e:
            raise e

    def create_file(path, file_content=""):
        try:
            with open(path, "w", encoding="utf-8") as w:
                w.write(file_content)
            logging.info(f"创建文件：{path}")
            return 0
        except Exception as e:
            raise e from FileNotFoundError

    demo_example_json = """{
  "login": [
    {
      "prob": 1,
      "activity": "lms2.xz.act.app_v4.account.LoginActivityV4",
      "times": 1,
      "actions": [
        {
          "xpath": "//*[@resource-id='lms2.xz.act:id/tv_account']",
          "action": "CLICK",
          "throttle": 2000
        }
      ]
    },
    {
      "prob": 1,
      "activity": "lms2.xz.act.app_v4.account.AccountLoginActivityV4",
      "times": 1,
      "actions": [
        {
          "xpath": "//*[@resource-id='lms2.xz.act:id/et_select']",
          "action": "CLICK",
          "throttle": 2000
        },
        {
          "xpath": "//*[@resource-id='lms2.xz.act:id/et_search']",
          "action": "CLICK",
          "text": "*测试酒店",
          "clearText": false,
          "throttle": 2000
        },
        {
          "xpath": "//*[@resource-id='lms2.xz.act:id/group_name']",
          "action": "CLICK",
          "throttle": 2000
        }
      ]
    }
  ]
}
    """
    demo_variable = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : {time.strftime("%Y/%m/%d %H:%M")}
# @Author  : Lifeng
# @Site    : 
# @File    : debugfeng.py
# @Software: PyCharm

from pathlib import Path

# 获取工程目录根路径    
DIR_PATH = Path(__file__).parent.parent
    """

    if os.path.isdir(project_name):
        logging.warning(
            f"{project_name} -> 文件夹已存在，请新建一个文件夹！"
        )
        return 0

    elif os.path.isfile(project_name):
        logging.warning(
            f"{project_name} -> 文件已存在，请新建一个文件！"
        )
        return 0

    create_folder(project_name)
    create_file(
        os.path.join(project_name, "../__init__.py"),
        f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : {time.strftime("%Y/%m/%d %H:%M")}
# @Author  : Lifeng
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm
        """
    )
    create_folder(os.path.join(project_name, "modules"))
    create_file(
        os.path.join(project_name, "modules", "dfwsgroup.json"),
        demo_example_json
    )
    create_file(
        os.path.join(project_name, "debugfeng.py"),
        demo_variable
    )


def main_scaffold(args):
    sys.exit(create_scaffold(args.project_name))
