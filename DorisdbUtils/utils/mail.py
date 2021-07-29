# -*- coding:utf-8 -*-
import smtplib
from log_handler import MyLog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Sendmail(object):

    def __init__(self, mail_list=[]):
        self.mail_user = "xxx@163.com"
        self.mail_passwd = "xxx"
        self.mail_list = list(set(mail_list))
        self.smtp_server = 'smtp.163.com'
        self.logger = MyLog().logger

    def send_mail(self, mail_content, mail_subject):
        mail_from = self.mail_user
        msg = MIMEMultipart('related')
        msgtext = MIMEText(mail_content, 'html', 'utf-8')

        msg.attach(msgtext)
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ";".join(self.mail_list)
        try:
            s = smtplib.SMTP()
            s.connect(self.smtp_server, 25)
            s.ehlo("hello")
            s.login(self.mail_user, self.mail_passwd)
            s.sendmail(mail_from, self.mail_list, msg.as_string())
            s.close()
            print ("发送邮件给%s成功" % self.mail_list)
        except Exception as e:
            print ("发送邮件给%s失败" % self.mail_list)
            print (e)