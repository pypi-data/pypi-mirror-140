#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/17 18:28
# @Author  : Lifeng
# @Site    : 
# @File    : custom.py
# @Software: PyCharm

import json
import logging
from pathlib import Path


class _HandleFile:

    @staticmethod
    def _get_path(folder: str, filename: str):
        return Path(__file__).parent.parent.joinpath(folder, filename)

    def read_json(self, folderpath, filename, module_name):
        """
        读取filename文件中的文件
        :param folderpath:
        :param filename:
        :param module_name:
        :return:
        """
        with open(self._get_path(folderpath, filename), encoding="utf-8") as r:
            data = json.loads(r.read())
            results = data[module_name]
            logging.info(f"文件数据读取成功-> {filename}")
            return results

    def write_json(self, data, filename):
        """
        往config文件夹中的文件写入数据
        :param data:
        :param filename:
        :return:
        """
        try:
            with open(self._get_path("config", filename), mode="w", encoding="utf-8", ) as w:
                json.dump(data, w)
            logging.info(f"文件数据写入成功-> {filename}")
            return 0
        except Exception as e:
            raise e from FileNotFoundError

    def clear_json(self, filename):
        """
        清空config文件夹中文件的数据
        :param filename:
        :return:
        """
        try:
            with open(self._get_path("config", filename), mode="w") as c:
                c.truncate(0)
            logging.info(f"文件数据清除成功-> {filename}")
            return 0
        except Exception as e:
            raise e from FileNotFoundError


def max_xpath_actions(folderpath, filename, module_name):
    """
    自定义文件数据写入
    :param folderpath:
    :param filename:
    :param module_name:
    :return:
    """
    handle = _HandleFile()
    try:
        data = handle.read_json(folderpath, filename, module_name)
        handle.write_json(data, "max.xpath.actions")
        return 0
    except Exception as e:
        raise e from FileNotFoundError


def max_xpath_actions_clear():
    """
    自定义文件清空
    :return:
    """
    try:
        handle = _HandleFile()
        handle.clear_json("max.xpath.actions")
        return 0
    except Exception as e:
        raise e from FileNotFoundError


def max_config(filename, name):
    """
    随机输入字符串
    :param filename:
    :param name:
    :return:
    """
    handle = _HandleFile()
    data = handle.read_json(filename, name)
    handle.write_json(data, "max.config")


def max_strings(filename, name):
    """
    从文件中随机读取字符串输入
    :param filename:
    :param name:
    :return:
    """
    handle = _HandleFile()
    data = handle.read_json(filename, name)
    handle.write_json(data, "max.strings")


def awl_strings(filename, name):
    """
    处理白名单
    :param filename:
    :param name:
    :return:
    """
    handle = _HandleFile()
    data = handle.read_json(filename, name)
    handle.write_json(data, "max.strings")


def abl_strings(filename, name):
    """
    处理黑名单
    :param filename:
    :param name:
    :return:
    """
    handle = _HandleFile()
    data = handle.read_json(filename, name)
    handle.write_json(data, "max.strings")
