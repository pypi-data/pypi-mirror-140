# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2022/2/14 20:46
# @Author: "John"

from datetime import datetime
from os.path import basename

from mob_tools import logger
from mob_tools._get_frame import get_frame

"""
基于loguru的日志模块
"""


def formatted_mob_msg(msg, level, class_name='', func_name='', line_num='', track_id=''):
    """
    :param msg:         日志内容
    :param level:       日志级别
    :param class_name:  调用模块
    :param line_num:    调用行号
    :param func_name:  调用方法名称
    :param track_id:    trackId
    :return:            格式化后的日志内容
    """
    formatted_level = '{0:>8}'.format(f'{level}')
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    formatted_msg = f'[{ts} {formatted_level}] {class_name}.{func_name}:{line_num} {msg} {track_id}'
    return formatted_msg


class MobLoguru:

    def __init__(self, deep=1):
        """

        :param deep:           获取调用者文件名、方法名、行号深度
        """
        self._msg = ''
        self._level = ''
        self._track_id = ''
        self._deep = deep

    def debug(self, msg):
        self._msg = msg
        self._level = 'DEBUG'
        return self

    def info(self, msg):
        self._msg = msg
        self._level = 'INFO'
        return self

    def warning(self, msg):
        self._msg = msg
        self._level = 'WARNING'
        return self

    def error(self, msg):
        self._msg = msg
        self._level = 'ERROR'
        return self

    def critical(self, msg):
        self._msg = msg
        self._level = 'CRITICAL'
        return self

    def track_id(self, track_id):
        frame = get_frame(self._deep)
        self._track_id = track_id
        msg = formatted_mob_msg(
            self._msg,
            self._level,
            basename(frame.f_code.co_filename),  # 脚本名称
            frame.f_code.co_name,  # 方法名
            str(frame.f_lineno),  # 行号
            self._track_id
        )

        logger.log(self._level, msg)
        return self

    def commit(self):
        pass
