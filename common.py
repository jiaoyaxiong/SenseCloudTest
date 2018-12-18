#encoding:utf-8


import ConfigParser
import os
import requests
import logging
import time

class sensemediaTestBase(object):
    def __init__(self,testid):
        self.testid=testid



    def setlogger(self,name):
        now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        date_ymd = time.strftime('%Y%m%d', time.localtime(time.time()))
        ymd_dir="/data/sensetestlog/%s" % date_ymd
        if not os.path.exists(ymd_dir):
            os.mkdir(ymd_dir)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level=logging.INFO)
        self.handler = logging.FileHandler("/data/sensetestlog/%s/%s.log" % (date_ymd,self.testid+"_"+now))
        self.handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)

        self.console = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        self.console.setFormatter(self.formatter)

        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.console)
        self.logger.info("logger init pass")


#获取config配置文件
def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/config.conf'
    config.read(path)
    return config.get(section, key)


if __name__ == "__main__":
    print type(getConfig("url","video_tag_common"))
#其中 os.path.split(os.path.realpath(__file__))[0] 得到的是当前文件模块的目录