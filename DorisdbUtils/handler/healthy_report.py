# -*- coding: utf-8 -*-

import datetime
#from utils import mail
import db_hanlder
from prettytable import PrettyTable
from utils import config_parser
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class BaseCheck(object):

    def __init__(self, user="", host="", db="", passwd="", port=9030):
        self.table_black_list = []
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

    def get_alldbs(self):
        sql = "show databases;"
        return self.db.query(sql)

    def get_alltables(self):
        valid_tables = []
        sql = "show table status;"
        tables_info = self.db.query(sql)
        for table in tables_info:
            if table[-1] == "OLAP":
                valid_tables.append(table[0])
        return valid_tables

    def get_table_info(self, table):
        buckets = 0
        data_size = 0
        sql = "show partitions from %s;" % table
        infos = self.db.query(sql)
        for line in infos:
            if "B" not in line[-2]:
                continue
            buckets += int(line[9])
            data_size_split = line[-2].split()
            data_size += float(data_size_split[0])*(self.convert(data_size_split[1]))
        return {
            "Buckets": buckets,
            "DataSize": data_size
        }

    def table_healthy(self):
        tables_info = []
        tables = self.get_alltables()
        for table in tables:
            if table in self.table_black_list:
                continue
            if not self.get_table_info(table):
                continue
            if not self.get_table_info(table)["Buckets"]:
                continue
            tables_info.append({
                "name": table,
                "DataSize": self.get_table_info(table)["DataSize"],
                "Buckets": self.get_table_info(table)["Buckets"],
                "point": self.get_table_info(table)["DataSize"] / int(self.get_table_info(table)["Buckets"])
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
    config = config_parser.Parser("../config.ini")
    #收件人
    # mail = mail.Sendmail(['xxx@xxx.com'])
    #DorisDB相关配置
    table_format = PrettyTable(['库名', '表名', '表数据量(/GB)', 'Tablet数', '单Tablet数据量(/GB)'])
    for database in config['databases'].split(','):
        base_check = BaseCheck(user=config['user'], host=config['fe_host'],
                               db=database, port=int(config['port']), passwd=config['password'])
        tables = base_check.table_healthy()
        tables_info = sorted(tables, key=lambda i: i['Buckets'], reverse=True)
        for table in tables_info:
            table_format.add_row([database, table['name'], table['DataSize'], table['Buckets'], table['point']])
    print table_format
    # mail_content, mail_subject = generate_template(tables_info)
    # mail.send_mail(mail_content, mail_subject)