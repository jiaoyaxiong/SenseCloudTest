# encoding:utf-8
import sys

sys.path.append("..")
import common
import os
import requests
import uuid
import json
from requests_toolbelt import MultipartEncoder
from nose.plugins.attrib import attr

"""
用例名字：test_video_abnormal_010
测试目的：测试其他格式视频rtsp
预置条件：1，测试桩已启动（接收callback 的post 请求）
         2,私有云已启动
         3,视频文件:  已经放到当前目录
测试步骤：1，构造请求发送最大size 的MP4 视频给私有云分析
         2，检查响应
预期结果：1，响应状态码200
         2，应答结果检查：
         3，callback ...

content-type:multipart/form-data

"""


@attr(feature="test_video_type_common")
@attr(runtype="abnormal")
@attr(videotype="normal")
class test_video_abnormal_010(common.sensemediaTestBase):

    def __init__(self):
        super(test_video_abnormal_010, self).__init__("test_video_abnormal_010")
        common.sensemediaTestBase.setlogger(self, __name__)

        #超时时间(任务需在自指定时间内完成，否则置为失败),检测间隔为test_interval
        self.expire = 300
        self.test_interval = 5

        #请求url
        self.url = common.getConfig("url", "cloud_url")
        self.logger.info("testcase is %s " % self.testid)
        self.logger.info("cwd is %s " % os.getcwd())
        self.logger.info("request url is %s" % self.url)

        # get_res_url(通过此url 查询任务状态)
        self.res_url = common.getConfig("url", "res_url")

        # request url
        #self.file =("renmingdemingyi.avi", open('/codes/sensecloud/test_video_type_common/renmingdemingyi.avi', 'rb'), "video/mpeg4")
        # TODO
        self.video_url = "https://172.20.8.15:6554/renmingdemingyi.avi"
        self.stream = "rtsp://172.20.8.15:8081/bucunzai.ts"
        self.frame_extract_interval = ""
        self.modules = ""
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = ""

        # 请求体
        self.body = {
            "stream": self.stream,
            "callback": self.callback,
            "token": self.token
        }
        # 请求头
        self.headers = {'content-type': 'application/json'}


        #期望使用的modules
        self.expect_modules=["filter_celebrity",]
        #probability 最低限度
        self.probability_low=0
        #probability 最高限度
        self.probability_high=1

    def setup(self):
        self.logger.info("test setup")

    def test_001(self):

        self.logger.info("now to send request,body is  %s!" % self.body )

        # 发送request请求
        r = requests.post(self.url, data=json.dumps(self.body), headers=self.headers)

        self.logger.info(r.text)

        # 检查http 状态码
        if r.status_code == requests.codes.ok:
            self.logger.error("status code is %s,not as expected" % r.status_code)
            assert False
        self.logger.info("status code is %s" % r.status_code)

        if r.json().get("http_code") == 500:
            self.logger.error("status code is %s,not as expected" % r.status_code)
            assert False

        if r.json().get("error_msg") != "Request stream is invalid":
            assert False

        if r.json().get("http_code") != 400:
            assert False

        if r.json().get("error_code") != 1010108:
            assert False

        if r.json().get("status") != "error":
            assert False





    def teardown(self):
        self.logger.info("test teardown")
