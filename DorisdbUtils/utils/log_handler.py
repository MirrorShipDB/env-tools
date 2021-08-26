import os
import logging

class MyLog(object):
    def __init__(self, fmt=None, level=None, path=None, mode="file"):
        self.path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.logger = logging.getLogger(path)
        self.__init__formatter(fmt)
        self.__init__level(level)
        self.__init__mode(mode)


    def __init__formatter(self, fmt):
        if fmt:
            self.formatter = logging.Formatter(fmt)
        else:
            self.formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

    def __init__level(self, level):
        if level:
            self.logger.setLevel(level)
        else:
            self.logger.setLevel(logging.INFO)

    def __init__mode(self, mode):
        if mode == "file":
            if self.path:
                filelogger = logging.FileHandler(self.path + "/report.log")
            else:
                self.path = "/home/dorisdb/report.log"
                filelogger = logging.FileHandler(self.path)
            filelogger.setFormatter(self.formatter)
            self.logger.addHandler(filelogger)
        else:
            cmdlogger = logging.StreamHandler()
            cmdlogger.setFormatter(self.formatter)
            self.logger.addHandler(cmdlogger)