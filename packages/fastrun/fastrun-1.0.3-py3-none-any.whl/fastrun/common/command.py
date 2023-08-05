#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 21:14
# @Author  : Lifeng
# @Site    : 
# @File    : command.py
# @Software: PyCharm

import os
import sys
from loguru import logger
from pathlib import Path
from fastrun.android.script import StabilityTestAndroid
from fastrun.common.custom import max_xpath_actions, max_xpath_actions_clear


def init_parser_command(subparsers):
    sub_parser_command = subparsers.add_parser(
        "run", help="运行"
    )
    sub_parser_command.add_argument(
        "package", type=str, nargs="?", help="包名"
    )
    sub_parser_command.add_argument(
        "-m", "--minutes", type=int, help="指定分钟-可选参数"
    )
    sub_parser_command.add_argument(
        "-module", "--modulename", type=str, help="指定被读取文件中的变量名称（自定义的模块名）-可选参数"
    )
    sub_parser_command.add_argument(
        "-t", "--throttle", type=int, help="遍历事件频率(建议为500-800)-可选参数"
    )
    sub_parser_command.add_argument(
        "-l", "--log", default=True, action="store_true", help="存储日志"
    )

    return sub_parser_command


def main_command(args):
    # 清空文件\config\max.xpath.actions文件的数据
    max_xpath_actions_clear()
    # 判断是否为真值
    if args.modulename:
        logger.info(f"获取默认指定json文件中的模块名：{args.modulename}")

        # 根据脚本运行路径，获取根目录下的目录树，取到对应的工程目录
        default_json_path = tuple(
            root for (root, _, _) in os.walk(sys.path[0])
        )[-1]

        logger.info(f"获取默认指定json文件路径：{default_json_path}")
        logger.info(f"获取默认指定json文件路径及名称：{Path(default_json_path).joinpath('dfwsgroup.json')}")

        # 根据获取的路径json文件路径及模块名称，进行数据写入操作
        max_xpath_actions(default_json_path, "dfwsgroup.json", args.modulename)

    if args.package:
        logger.info(f"指定包名-> {args.package}")

        minutes, throttle = args.minutes, args.throttle

        if minutes or throttle:
            logger.info(f"指定分钟-> {minutes}")
            logger.info(f"指定事件频率-> {throttle}")
        else:
            minutes, throttle = 5, 500
            logger.info(f"默认分钟-> {minutes}")
            logger.info(f"默认事件频率-> {throttle}")

        if not args.log:
            logger.info(f"关闭日志获取-> {args.log}")

        logger.info(f"开始运行命令")
        return os.system(StabilityTestAndroid().execute(packages=args.package, minutes=minutes, throttle=throttle,
                                                        is_command=args.log))
    else:
        raise Exception(f"请检查包名-> {args.package}")

if __name__ == '__main__':
    print(Path(__file__).parent.parent)