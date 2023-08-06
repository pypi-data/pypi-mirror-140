import datetime
import requests
import time
from cyclonefw.core.utils import getLogger

storageLogger = getLogger("storage")


def write(filename, data, timeout=600, service="http://oss.storage.svc.cluster.local"):
    """
    存储文件到文件存储服务器中
    :param timeout: 超时时间, 单位秒
    :param filename: 文件名称
    :param data: 文件数据,所有格式数据按照二进制处理
    :param service: 文件服务器地址, 在k8s中可不填写
    :return:
    """
    start = int(time.time())
    finalName = "{}_{}".format(filename, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))
    try:
        requests.post("{}/postUpload".format(service), headers={"filename": finalName}, data=data, timeout=timeout)
        storageLogger.info("文件: %s, id: %s, 大小: %s, 存储成功, 用时: %s", filename, finalName, len(data), int(time.time()) - start)
        return finalName
    except Exception as e:
        storageLogger.error("文件: %s 存储错误: %s", filename, e)
        raise e


def read(filename, timeout=600, service="http://oss.storage.svc.cluster.local"):
    """
    从文件存储中读文件
    :param timeout: 超时时间, 单位秒
    :param filename: 文件名称
    :param service: 文件服务器地址, 在k8s中可不填写
    :return:
    """
    start = int(time.time())
    try:
        resp = requests.get("{}/getFile?name={}".format(service, filename), timeout=timeout)
        storageLogger.info("文件: %s, 大小: %s, 读取成功, 用时: %s", filename, len(resp.content), int(time.time()) - start)
        return resp.content
    except Exception as e:
        storageLogger.error("文件: %s 读取错误: %s", filename, e)
        raise e
