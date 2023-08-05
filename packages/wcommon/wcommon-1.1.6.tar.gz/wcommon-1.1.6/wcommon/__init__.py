# coding=utf-8
from __future__ import division
import time as t
import datetime
from tkinter.messagebox import NO
import requests
import json
import subprocess
import socket
import traceback
import os
import sys
import pymysql
import configparser
from loguru import logger
# reload(sys)
# sys.setdefaultencoding('utf8')
# print("WARN:please configuration the configuraion_file variable")

configuraion_file = "/data/apps/public/conf.ini"

def getConfig():
    print(configuraion_file)
    import configparser
    config = configparser.ConfigParser()
    config.read(configuraion_file)
    return config


# for python2
# def execute_command2(cmd):
#     status,output = commands.getstatusoutput(cmd)
#     if status == 0:
#         status = True
#     else:
#         status = False
#
#     tempLines = output.split("\n")
#
#     lines = []
#
#     for e in tempLines:
#         t = e.strip()
#         if len(t) >0 :
#             lines.append(t)
#
#     return (status, output, lines)


# for python3
def execute_command3(cmd):
    status, output = subprocess.getstatusoutput(cmd)
    if status == 0:
        status = True
    else:
        status = False

    tempLines = output.split("\n")

    lines = []

    for e in tempLines:
        t = e.strip()
        if len(t) > 0:
            lines.append(t)

    return (status, output, lines)


# 如果subprocess.getstatusoutput出现乱码而失败，就使用这个方法执行命令
def execute_command_use_os(cmd):
    r = os.system(cmd)
    return r


# 执行shell命令,并返回结果
def execute_command(cmd):
    major = sys.version_info[0]
    if major == 2:
        # return execute_command2(cmd)
        pass
    else:
        return execute_command3(cmd)


# 将datetime转为timestamp
def timestamp(dt):
    return int(t.mktime(dt.timetuple()))


def parseCommandArguments(args):
    argDict = {}
    for argument in args:
        print("argument:" + argument)
        if argument.startswith("-D"):
            arg = argument[2:]

            idx = arg.find("=")

            k = arg[0:idx]
            v = arg[idx + 1:]
            argDict[k] = v
    return argDict


def wait_unitl(futureTimestamp, msg=""):
    print("futureTimestamp %s " % (futureTimestamp))

    now = datetime.datetime.now()
    nowTimestamp = timestamp(now)

    print("nowTimestamp %s " % (nowTimestamp))

    if nowTimestamp < futureTimestamp:
        d = futureTimestamp - nowTimestamp
        t.sleep(d)


# 获取redisCluster的对象
# def getRedisCluster(redisClusterStr):
#     from rediscluster import StrictRedisCluster
#     print(redisClusterStr)
#     redisCluster = []
#     for nodePort in redisClusterStr.split(","):
#         kv = nodePort.split(":")
#         node = {"host": kv[0], "port": kv[1]}
#         redisCluster.append(node)
#
#     print(redisCluster)
#     rc = StrictRedisCluster(startup_nodes=redisCluster, decode_responses=True)
#     return rc


# 获取文件的创建时间
def getFileCreateTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getctime(filePath)
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的访问时间
def getFileAccessTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getatime(filePath)
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


# 获取文件的修改时间
def getFileModifyTime(filePath):
    # filePath = unicode(filePath,'utf8')
    t = os.path.getmtime(filePath)
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def getHost(url):
    beginIndex = url.find("//")
    endIndex = url.find("/", beginIndex + 2)
    host = url[beginIndex + 2:endIndex]
    return host


def getHostname(url):
    beginIndex = url.find("//")
    endIndex = url.find(":", beginIndex + 2)
    if endIndex < 0:
        endIndex = url.find("/", beginIndex + 2)
    hostname = url[beginIndex + 2:endIndex]
    return hostname


def getFileSize(filePath):
    fsize = os.path.getsize(filePath)
    return fsize


def getFilePrefix(path):
    return os.path.splitext(path)[0]


def getFilePostfix(path):
    return os.path.splitext(path)[1][1:]


def getLocalHostname():
    hostname = ""
    try:
        hostname = socket.gethostname()
    except:
        traceback.print_exc()
    return hostname


def getLocalIp():
    ip = ""
    try:
        # ip=socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        traceback.print_exc()
    return ip


def ding_send_text(message, token=None, mobiles=[], is_at_all=False):
    from dingtalkchatbot.chatbot import DingtalkChatbot

    if not token:
        config = getConfig()
        token = config.get("dingding", "token")

    # WebHook地址
    webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' + token
    # 初始化机器人小丁
    xiaoding = DingtalkChatbot(webhook)
    if is_at_all:
        xiaoding.send_text(msg=message, is_at_all=True)
    elif mobiles and len(mobiles) > 0:
        xiaoding.send_text(msg=message, is_at_all=False, at_mobiles=mobiles)
    else:
        xiaoding.send_text(msg=message, is_at_all=False)


def eweixin_send_text(message, token=None, mobiles=[], is_at_all=False):
    if not token:
        config = getConfig()
        token = config.get("dingding", "token")
    data = json.dumps({"msgtype": "text", "text": {"content": message, "mentioned_mobile_list": mobiles}})
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + token, data,
                  auth=('Content-Type', 'application/json'))


class Mysql():

    def __init__(self, configuraion_file="/data/apps/public/conf.ini", section="mysql"):
        self.database = None
        try:
            config = configparser.ConfigParser()
            config.read(configuraion_file)
            host = config.get(section, "host")
            port = int(config.get(section, "port"))
            user = config.get(section, "user")
            password = config.get(section, "passwd")
            database_str = config.get(section, "database")
            charset = config.get(section, "charset")

            self.database = pymysql.connect(host=host, port=port, user=user, passwd=password, db=database_str,
                                            charset=charset, autocommit=True,
                                            cursorclass=pymysql.cursors.DictCursor)
        except ImportError:
            print("Error: configparser or pymysql module not exists")
        except:
            traceback.print_exc()


    def query(self, sql, argumentTuple=(), timestamp2str=True):
        self.database.ping()
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        rows = []

        if timestamp2str:
            timesamp_field_array = []
            for tp in cursor.description:
                if tp[1] == pymysql.constants.FIELD_TYPE.TIMESTAMP:
                    timesamp_field_array.append(tp[0])

            for row in cursor:
                for field in timesamp_field_array:
                    tmp_value = row[field].strftime("%Y-%m-%d %H:%M:%S")
                    row[field] = tmp_value
                rows.append(row)
        else:
            for row in cursor:
                rows.append(row)
        return rows


    def insert(self, tableName, dic, commit=True):
        self.database.ping()
        cursor = self.database.cursor()
        cols = []
        vals = []
        placeholders = []
        id = ""
        for key in dic.keys():
            val = dic[key]
            if val != None:
                cols.append(key)
                placeholders.append("%s")
                vals.append(val)
        insertSql = "INSERT INTO " + tableName + " ( %s ) VALUES ( %s )" % (",".join(cols), ",".join(placeholders))
        logger.debug(insertSql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(insertSql, tuple(vals))
            id = cursor.lastrowid
        if commit:
            self.database.commit()

        return id


    def update_by_id(self, tableName, id, dic, idFieldName="id", commit=True):
        self.database.ping()
        cursor = self.database.cursor()
        vals = []
        placeholders = []
        for key in dic.keys():
            val = dic[key]
            if val != None:
                placeholders.append("{} = %s ".format(key))
                vals.append(val)
        setting = " , ".join(placeholders)
        vals.append(id)
        updateSql = "update {0} set {1} where {2} = %s ".format(tableName, setting, idFieldName)
        logger.debug(updateSql)

        if commit:
            logger.debug(tuple(vals))
            cursor.execute(updateSql, tuple(vals))
        if commit:
            self.database.commit()


    def execute(self, sql, argumentTuple=(), commit=True):
        self.database.ping()
        cursor = self.database.cursor()
        logger.debug("query sql:\t%s, arguments: %s" % (sql, argumentTuple))
        if len(argumentTuple) == 0:
            cursor.execute(sql)
        else:
            cursor.execute(sql, argumentTuple)
        if commit:
            self.database.commit()


    def delete(self, sql, commit=True):
        self.database.ping()
        cursor = self.database.cursor()
        logger.debug("delete sql:\t" + sql)
        if commit:
            cursor.execute(sql)
            self.database.commit()