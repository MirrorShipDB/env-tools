# -*- coding: UTF-8 -*-
import pymysql
from utils import log_handler

class DbHanlder():
    def __init__(self, user, passwd="", db="", host="localhost", port=9030):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.dbName = db
        self.charset = "utf8"
        self.logger = log_handler.MyLog().logger

    def open(self):
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.passwd,
                db=self.dbName,
                port=self.port,
                charset=self.charset,
            )
        except pymysql.err.OperationalError as e:
            self.logger.exception("数据库连接失败！")
            if "Errno 10060" in str(e) or "2003" in str(e):
                self.logger.error("数据库连接失败！")
            raise
        self.logger.info("数据库连接成功")
        self.currentConn = conn  # 数据库连接完成
        self.cursor = self.currentConn.cursor()  # 游标，用来执行数据库

    def close(self):  # 关闭连接
        self.logger.info("关闭数据库连接")
        if self.cursor:
            self.cursor.close()
        self.currentConn.close()

    def query(self, sql):
        data = ()
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
        except Exception as e:
            self.logger.error(e.message)
        return data

    def query_many(self, sql):
        data = ()
        try:
            self.cursor.executemany(sql)
            data = self.cursor.fetchmany()
        except Exception as e:
            self.currentConn.rollback()
            self.logger.error(e.message)
        return data


    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.currentConn.commit()
        except Exception as e:
            self.currentConn.rollback()
            self.logger.error(e.message)
        self.close()
