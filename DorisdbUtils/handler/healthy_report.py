# -*- coding: utf-8 -*-

import datetime
from utils import mail
import db_hanlder
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class BaseCheck(object):

    def __init__(self, user="", host="", db="", passwd="", port=9030):
        self.db = db_hanlder.DbHanlder(user, passwd=passwd,
                                       host=host, db=db, port=port)
        self.db.open()

    def convert(self, item):
        capacity_dict = {
            "B": round(1/1024.0/1024/1024, 3),
            "KB": round(1/1024.0/1024, 3),
            "MB": round(1/1024.0, 3),
            "GB": 1,
            "TB": 1*1024,
            "PB": 1*1024*1024
        }
        return capacity_dict[item]

    def get_alltables(self):
        sql = "show tables;"
        return self.db.query(sql)

    def get_table_info(self, table):
        sql = "show partitions from %s;" % table
        info = self.db.query(sql)[0]
        if "B" not in info[-2]:
            return {}
        data_size = info[-2].split()
        return {
            "Buckets": info[9],
            "DataSize": float(data_size[0])*(self.convert(data_size[1]))
        }

    def table_healthy(self):
        tables_info = []
        tables = self.get_alltables()
        for table in tables:
            if 'hive_demo_jd' in table[0]:
                continue
            if not self.get_table_info(table[0]):
                continue
            tables_info.append({
                "name": table[0],
                "DataSize": self.get_table_info(table[0])["DataSize"],
                "Buckets": self.get_table_info(table[0])["Buckets"],
                "point": self.get_table_info(table[0])["DataSize"] / int(self.get_table_info(table[0])["Buckets"])
            })

        return tables_info


def generate_template(tables):
    mail_content = ""
    CSS_STYLE = """<style type="text/css">
                     #avail {
                       font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
                       border-collapse: collapse;
                       width: 100%;
                     }
                     #avail th {
                       font-size: 14px;
                       border-collapse: collapse;
                       border: 1px solid #000000;
                       background-color: #cccccc;
                        width: auto;
                     }
                     #avail td {
                       font-size: 13px;
                       border-collapse: collapse;
                       border: 1px solid #000000;
                       text-align: center;
                       width: auto;
                     }
                     </style>"""
    mail_subject = datetime.datetime.now().strftime('%Y-%m-%d') + "日巡检"
    mail_header = "<html><head>" + CSS_STYLE + '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">' + "</head><body>"
    mail_title = '<h1 align="center">' + datetime.datetime.now().strftime('%Y-%m-%d') + "日巡检结果</h1>"
    mail_tail = '</body></html>'
    table_header = generate_mail_table_header()
    mail_body = "<tbody>"
    for table in tables:
        mail_body += "<tr>"
        mail_body += "<td align='left'>" + table['name'] + "</td>"
        mail_body += "<td align='left'>" + table['Buckets'] + "</td>"
        mail_body += "<td align='left'>" + str(table['DataSize']) + "</td>"
        if table['point'] < 1 or table['point'] > 10:
            mail_body += "<td align='left' bgcolor='red'>" + str(table['point']) + "</td>"
        else:
            mail_body += "<td align='left'>" + str(table['point']) + "</td>"
        mail_body += "</tr>"
    mail_body += '</tbody>'
    mail_content = mail_header + mail_title + table_header + mail_body + mail_tail
    return (mail_content, mail_subject)

def generate_mail_table_header():
    table_header = '''<table id='avail' cellpadding="1" cellspacing="1" border="1">'''
    table_header += '</tr><tr>'
    table_header += '<th>Table</th><th>Bucket数</th><th>表数据量(/GB)</th><th>单Bucket数据量(/GB)</th>'
    table_header += '</tr>'
    return table_header

if __name__ == "__main__":
    #收件人
    mail = mail.Sendmail(['xxx@xxx.com'])
    #DorisDB相关配置
    base_check = BaseCheck(user="xxx", host="x.x.x.x", db="xxx", port=9030, passwd="")
    tables = base_check.table_healthy()
    tables_info = sorted(tables, key=lambda i: i['point'])
    mail_content, mail_subject = generate_template(tables_info)
    mail.send_mail(mail_content, mail_subject)