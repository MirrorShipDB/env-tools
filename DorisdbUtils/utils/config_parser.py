import configparser

def Parser(file_name):
    commonConf = {}
    conf = configparser.ConfigParser()
    conf.read(file_name, encoding='utf-8')
    sections = conf.sections()
    for section in sections:
        commonConf[section] = dict(conf.items(section))
    return commonConf


# test
# def test():
#     print Parser("../config.ini")

# test()
