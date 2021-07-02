#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2021/5/25 15:36
# @Author : shl
# @File : dingding_notice.py
# @Desc :钉钉机器人预警消息推送
import inspect
import logging
import os
import sys
import time
import requests
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


class Logger(object):
    """
    日志类
    """

    def __init__(self):
        self.__loggers = {}
        self.logs_dir = os.path.abspath('.')
        self.handlers = self.create_handlers()
        self.levels = self.handlers.keys()
        self.stream_handler()

    def stream_handler(self):
        for level in self.levels:
            logger = logging.getLogger(str(level))
            formatter = logging.Formatter()
            console = logging.StreamHandler()  # 输出到控制台的handler
            console.setFormatter(formatter)
            console.setLevel('INFO')
            logger.addHandler(console)
            logger.addHandler(self.handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level: logger})

    @staticmethod
    def log_message(level, message):
        _stack = inspect.stack()[2]
        filename = _stack.filename
        function = _stack.function
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return "[%s][%s][%s][%s]: %s" % (level, current_time, filename, function, message)

    def info(self, message):
        message = self.log_message('INFO', message)
        self.__loggers[logging.INFO].info(message)

    def error(self, message):
        message = self.log_message('ERROR', message)
        self.__loggers[logging.ERROR].error(message)

    def warning(self, message):
        message = self.log_message('WARNING', message)
        self.__loggers[logging.WARNING].warning(message)

    def debug(self, message):
        message = self.log_message('DEBUG', message)
        self.__loggers[logging.DEBUG].debug(message)

    def create_handlers(self):
        log_path = 'log\\{0}'.format(os.path.basename(sys.argv[0]).split(".")[0])
        for dir_path in ['{1}\\{0}'.format(msg_type, log_path) for msg_type in ['info', 'error', 'warning', 'debug']]:
            if not os.path.exists(os.path.join(self.logs_dir, dir_path)):
                os.makedirs(os.path.join(self.logs_dir, dir_path))
        day = datetime.now().strftime("%Y-%m-%d")
        handlers = {
            logging.INFO: os.path.join(self.logs_dir, f'{log_path}\\info\\{day}.log'),
            logging.ERROR: os.path.join(self.logs_dir, f'{log_path}\\error\\{day}.log'),
            logging.WARNING: os.path.join(self.logs_dir, f'{log_path}\\warning\\{day}.log'),
            logging.DEBUG: os.path.join(self.logs_dir, f'{log_path}\\debug\\{day}.log'),
        }
        levels = handlers.keys()
        for level in levels:
            if level == 20:
                path = os.path.abspath(handlers[level])
                handlers[level] = TimedRotatingFileHandler(path, when="D", backupCount=7, encoding='utf-8', interval=1)
            else:
                path = os.path.abspath(handlers[level])
                handlers[level] = TimedRotatingFileHandler(path, when="D", backupCount=30, encoding='utf-8', interval=1)
        return handlers


class DingTalkNotice(Logger):
    """
    钉钉机器人预警
    """

    def __init__(self, access_token, mobile=None):
        super(DingTalkNotice, self).__init__()
        self._token = access_token
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token={0}'
        self.mobile = mobile
        self.content = '[警告]'

    def send_msg(self, msg, log_print='info', mobile=None, at_all=False):
        try:
            if log_print == 'info':
                self.info(msg)
            elif log_print == 'warning':
                self.warning(msg)
            elif log_print == 'debug':
                self.debug(msg)
            else:
                self.error(msg)
            if (mobile or self.mobile) and not at_all:
                at_all = False
            else:
                at_all = True
            content = self.content + msg
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "isAtAll": at_all
                }
            }
            if mobile:
                phone_num = mobile
            elif not mobile and self.mobile:
                phone_num = self.mobile
            else:
                phone_num = ''
            if phone_num:
                data['at']['atMobiles'] = [phone_num]
            self.post(data)  # 接口推送
        except Exception as e:
            self.error("send_msg is not success msg:{0}".format(str(e)))

    def post(self, data):
        if self._token:
            url = self.url.format(self._token)
            req = requests.post(url, json=data)
            if req.status_code == 200:
                print(req.text)
            else:
                raise ValueError('钉钉接口异常！')


if __name__ == '__main__':
    DingTalkNotice(access_token='').send_msg(msg='测试消息')
