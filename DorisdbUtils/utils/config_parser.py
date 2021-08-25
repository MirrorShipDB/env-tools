import configparser

def Parser(file_name):
    conf = configparser.ConfigParser()
    conf.read(file_name, encoding='utf-8')
    commonConf = conf.items('common')
    commonConf = dict(commonConf)
    return commonConf


def test():
    print Parser("../config.ini")

test()