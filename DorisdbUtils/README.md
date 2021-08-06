# 巡检demo

## 依赖
pip -r requirements.txt

在utils/mail.py配置smtp服务器地址，可以配置smtp.163.com，不过需要在网易邮箱设置授权码，可查看网上教程
在handler/healthy_report.py中配置收件人和DorisDB集群相关信息即可

## 用法

python healthy_report.py
