#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 11:12
# @Author  : Lifeng
# @Site    : 
# @File    : cli.py
# @Software: PyCharm

import sys
import argparse
from loguru import logger
from dfwsgroup import __description__, __version__
from dfwsgroup.common.command import init_parser_command, main_command
from dfwsgroup.common.scaffold import main_scaffold, init_parser_scaffold


def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "-V", "--version", dest="version", action="store_true", help="show version"
    )

    subparsers = parser.add_subparsers()
    init_parser_scaffold(subparsers)
    init_parser_command(subparsers)
    args = parser.parse_args()

    if sys.argv[1] == "startproject":
        main_scaffold(args)
    elif sys.argv[1] == "run":
        sys.exit(main_command(args))
    elif sys.argv[1] in ["-V", "--version"]:
        if parser.parse_args().version:
            print(f"version：{__version__}")
    else:
        logger.error(f"{sys.argv[1:]}")
        raise Exception
