from flask import abort
import cyclonefw
import os, logging
from logging.handlers import RotatingFileHandler
import requests


def redirect_errors_to_flask(func):
    """
    This decorator function will capture all Pythonic errors and return them as flask errors.

    If you are looking to disable this functionality, please remove this decorator from the `apply_transforms()` module
    under the ImageProcessor class.
    """

    def inner(*args, **kwargs):
        try:
            # run the function
            return func(*args, **kwargs)
        except ValueError as ve:
            if 'pic should be 2 or 3 dimensional' in str(ve):
                abort(400, "Invalid input, please ensure the input is either "
                           "a grayscale or a colour image.")
        except TypeError as te:
            if 'bytes or ndarray' in str(te):
                abort(400, "Invalid input format, please make sure the input file format "
                           " is a common image format such as JPG or PNG.")

    return inner


class AppFilter(logging.Filter):
    def __init__(self):
        pass

    def filter(self, record):
        record.app_name = cyclonefw.core.app.context.app_name
        return True


def getLogger(name="component", formatter="[%(asctime)s] [%(pathname)s(line:%(lineno)d)] [%(levelname)s] %(message)s",
              logPath=None, level=logging.DEBUG):
    """
    获取logger

    日志记录使用如下格式: %s 等作为占位符

    print "My name is %s and weight is %d kg!" % ('Zara', 21)

    :param name: 日志名称
    :param formatter: 日志格式
    :param logPath: 日志目录, 默认为 logs目录下, 使用 . 可以指定当前执行目录
    :param level: 日志级别
    :return:
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        consolelog = logging.StreamHandler()
        consolelog.setFormatter(logging.Formatter(formatter))
        logger.addHandler(consolelog)
        logger.addFilter(AppFilter())

    if logPath != None:
        logger.addHandler(logHandler(name, formatter, logPath))

    return logger


def logHandler(name, logPath="logs",
               formatter="[%(asctime)s] [%(pathname)s(line:%(lineno)d)] [%(levelname)s] %(message)s"):
    if not os.path.exists(logPath):
        os.makedirs(logPath, exist_ok=True)
    handler = CyclonefwRotatingFileHandler("{}/{}.log".format(logPath, name), "a", 1024 * 1024 * 20, 10)
    handler.setFormatter(logging.Formatter(formatter))
    return handler


class CyclonefwRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        if hasattr(record, "trace_id"):
            self.setFormatter(logging.Formatter("[%(asctime)s] [%(trace_id)s] [%(app_name)s] [%(pathname)s(line:%(lineno)d)] [%(levelname)s] %(message)s"))

        super(CyclonefwRotatingFileHandler, self).emit(record)


def getHostnameAndIp():
    """
    获取hostname及ip地址
    :return: hostname, ip
    """
    import socket
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return hostname, ip


class WrapperDict(dict):
    def __init__(self, seq=None, **kwargs):
        self.logger = getLogger()
        super(WrapperDict, self).__init__(seq, **kwargs)

    def __getitem__(self, item):
        value = dict.__getitem__(self, item)
        if item == "b64":
            if isinstance(value, str) and value.startswith("http"):
                try:
                    dict.__setitem__(self, item, requests.get(value, timeout=600).text)
                except Exception as e:
                    self.logger.error("get b64 from url failed: %s" % value)
                    self.logger.error(e)

        if item == "b64s":
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], str) and value[0].startswith("http"):
                    for i in range(len(value)):
                        try:
                            value[i] = requests.get(value[i], timeout=600).text
                        except Exception as e:
                            self.logger.error("get b64 from url failed: %s" % value)
                            self.logger.error(e)

        return dict.__getitem__(self, item)
