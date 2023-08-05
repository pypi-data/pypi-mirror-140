#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/8 17:37
# @Author  : Lifeng
# @Site    : 
# @File    : handle.py
# @Software: PyCharm

import json
from pathlib import Path
from jinja2 import Template


class Handle:
    def __init__(self, devices: str, packages: str):
        self.devices = devices
        self.packages = packages
        self.path = Path(__file__).parent.parent.joinpath("data", "command.json")

    def read_command(self, minutes, throttle):
        """
        文件中读取命令，并进行替换操作
        :param minutes:
        :param throttle:
        :return:
        """
        with open(self.path, encoding="utf-8") as r:
            log_ingo, command = "", ""
            data = Template(r.read()).render(
                contents=[self.devices, self.packages, minutes, throttle]
            )
            info = json.loads(data)["command"]
            for v in info[0].values():
                command += v + " "
            for v in info[1].values():
                log_ingo += v + " "
        return command, log_ingo

    def command_get(self, minutes, throttle, is_command: bool):
        """
        获取命令后进行拼接
        :param minutes:
        :param throttle:
        :param is_command:
        :return:
        """
        command, log_ingo = self.read_command(minutes, throttle)
        return command.lstrip() + log_ingo.strip() if is_command else command.strip()
