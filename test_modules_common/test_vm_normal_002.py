# encoding:utf-8
import sys

sys.path.append("..")
import common
import os
import requests
import time
import uuid
import json
from requests_toolbelt import MultipartEncoder
from nose.plugins.attrib import attr

"""
用例名字：test_vm_normal_002
测试目的：http--MP4-普通电影
预置条件：1，测试桩已启动（接收callback 的post 请求）
         2,私有云已启动
         3,视频文件:  已经放到当前目录
测试步骤：1，构造请求发送http--MP4-普通电影视频给私有云分析
         2，检查响应,记录响应结果
预期结果：1，响应状态码200
         2，应答结果检查：
         3，callback ... 通过requestid 查询结果是否完成
         4，超时机制（(视频时长×(功能1超时倍数+功能2超时倍数+...+功能n超时倍数)*整体超时倍数) = 超时时长）

content-type:application/json

"""
@attr(feature="test_video_transports_common")
@attr(runtype="normal")
@attr(videotype="normal")
class test_vm_normal_002(common.sensemediaTestBase):

    def __init__(self):
        super(test_vm_normal_002, self).__init__("test_vm_normal_002")
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
        self.file = ""
        # TODO
        self.video_url = "http://172.20.6.104/video_1.mp4"
        self.stream = ""
        self.frame_extract_interval = ""
        self.modules = ""
        self.callback = "http://172.20.23.42:22222/callback"
        self.token = "bbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        self.db_name = ""

        # 请求体
        self.body = {
            "url": self.video_url,
            "callback": self.callback,
            "token": self.token,
            "modules": "filter_np"
        }
        # 请求头
        self.headers = {'content-type': 'application/json'}


        #期望使用的modules
        self.expect_modules=["filter_np",]
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
        if r.status_code != requests.codes.ok:
            self.logger.error("status code is %s" % r.status_code)
            assert False

        # 检查响应

        r_header = r.headers['content-type']
        self.logger.info("response content-type is %s" % r_header)

        r_encoding = r.encoding
        self.logger.info("response encoding is %s" % r_encoding)

        r_body = r.json()
        self.logger.info("response body_json is %s" % r_body)

        # 检查响应是否只有三个元素
        if len(r_body) != 3:
            self.logger.error("repsonse has  more or less than 3 keys ,not as expected!")
            assert False

        # 检查响应status 是否是string,以及内容是否合适，是否为空,是否两边有空格
        resp_status = r_body.get("status")
        if not isinstance(resp_status, basestring):
            self.logger.error("resp_status %s is not sting " % resp_status)
            assert False

        if resp_status != resp_status.strip():
            self.logger.error("resp_status %s has space,pls check！" % resp_status)
            assert False

        if len(resp_status.strip()) == 0:
            self.logger.error("resp_status %s len is 0 ,pls check！" % resp_status)
            assert False

        if resp_status != "success":
            self.logger.error("resp_status content : %s  is not as expect  ,pls check！" % resp_status)
            assert False

        # 检查响应id 是否是string,是否两边有空格,是否为空
        resp_id = r_body.get("request_id")
        if not isinstance(resp_id, basestring):
            self.logger.error("resp_id %s is not sting " % resp_id)
            assert False

        if resp_id != resp_id.strip():
            self.logger.error("resp_id %s has space,pls check！" % resp_id)
            assert False

        if len(resp_id.strip()) == 0:
            self.logger.error("resp_id %s len is 0 ,pls check！" % resp_id)
            assert False

        # 检查响应message 是否是string,是否两边含有空格，是否为空

        resp_message = r_body.get("message")
        if not isinstance(resp_message, basestring):
            self.logger.error("resp_message %s is not sting " % resp_message)
            assert False

        if resp_message != resp_message.strip():
            self.logger.error("resp_message %s has space,pls check！" % resp_message)
            assert False

        if len(resp_message.strip()) == 0:
            self.logger.error("resp_message %s len is 0 ,pls check！" % resp_message)
            assert False

        if resp_message != "Request submitted successfully":
            self.logger.error("resp_message content : %s  is not as expect  ,pls check！" % resp_message)
            assert False

        #二次响应！　必须提供接口查询是否任务完成

        end_time= self.expire


        #is_finish为1 代表已完成，0代表未完成
        is_finish=""
        req_par = resp_id
        times = 1
        while end_time > 0:

            # 检测是否完成
            self.logger.info("this is times : %s.test_interval is %s  " % (times,self.test_interval))
            r = requests.get(self.res_url+req_par)
            self.logger.info("query status by requestid resopnse is %s" % r.text)

            # 判断size个数
            size_num = r.json().get("size")
            if size_num != 1:
                self.logger.error(" please make sure why size is %s" % size_num)
                assert False

            stat = r.json().get("content")[0].get("status")
            if stat == "DONE":
                self.logger.info("task has finished  ")
                break
            else:
                self.logger.info("task not done ,status is %s" % stat )
            time.sleep(self.test_interval)
            end_time -= self.test_interval
            times += 1

        stat = requests.get(self.res_url + req_par).json().get("content")[0].get("status")

        if stat != "DONE":
            self.logger.error("task expire,expire time is %s ！" % self.expire)
            assert False


        #TODO(后续看一下docker logs收到的内容是否正确)
        #第三次响应，检查返回给客户的callback 内容
        r = requests.get(self.res_url+req_par+"/results")
        self.logger.info("single results reponse is %s " % r.text)
        sta = r.json().get("content")[0].get("status")
        if sta != "DONE":
            self.logger.error("status should be DONE, but is %s" % sta)
            assert False

        #检查request_id 是否与之前一致


        if r.json().get("content")[0].get("requestId") != resp_id:
            self.logger.error("request_id : %s is not equal before:%s  " % (r.json().get("content")[0].get("requestId"),resp_id))
            assert False


        #检查isFinish是否为1
        if type(r.json().get("content")[0].get("isFinished")) != int or int(r.json().get("content")[0].get("isFinished")) != 1  :
            self.logger.error(
                "is_finish should be 1 ,but is : %s" % r.json().get("content")[0].get("isFinished"))
            assert False


        #获取result_urls
        res_res_url=json.loads(r.json().get("content")[0].get("result")).get("result_urls")
        self.logger.info("result urls is %s " % res_res_url)
        if len(res_res_url) is 0 :
            self.logger.error("result urls is %s ,not as expected " % res_res_url)
            assert False


        #上个步骤获取的resut_urls 可能有多个（list），每5000 sucess 帧一个json 文件

        # 判断size个数
        size_num = r.json().get("size")
        if size_num != 1:
            self.logger.error(" pls make sure why size is %s" % size_num)
            assert False

        for res_url in res_res_url:
            self.check_result_urls(res_url,resp_id)


    def check_result_urls(self,res_res_url,resp_id):
        #第四次响应
        #判断获取的json数据是否符合规范
        #status":"success","request_id":"0608aaf4-0fff-48c4-8408-e656bb151c8e","succ_results":
        r_json = requests.get(res_res_url).json()

        #判断status
        if r_json.get("status") != "success":
            self.logger.error("status is %s ,not as expected!" % r_json.get("status"))
            assert False

        #判断request_id 和之前是否一致
        if r_json.get("request_id") != resp_id:
            self.logger.error("request_id is %s ,reso_id is %s ,not as expect!" % (r_json.get("request_id"),resp_id))
            assert False

        # TODO 判断success results (如何确认这个是符合要求的)
        #1，判断是否有使用指定module（列印出所有的module）

        #所有使用的modules
        modules=set()
        for item in r_json.get("succ_results"):
            #可能有多个模块的结果，所以有多个results
            for result in item.get("results"):
                    modules.add(result.get("module"))

        self.logger.info("there are %s module: %s" %(len(modules),modules))

        #仅仅可使用１个指定ｍｏｄｕｌｅ

        if len(modules) != 1:
            self.logger.error("there should only 1 modules ! but is : %s " % len(modules))
            assert False


        #判断是否包含指定modules
        for expect_module in self.expect_modules:
            if expect_module not in modules:
                self.logger.error(
                    "there should have module:%s ,but not find !" %expect_module)
                assert False
        #判断modules 个数是否正确
        if len(self.expect_modules) != len(modules):
            self.logger.error(
                "there should have %s modules.but only find %s modules"%(len(self.expect_modules),len(modules)))
            assert False

        #2，判断阈值是否在某个范围内(probability)
        for item in r_json.get("succ_results"):
            for result in item.get("results"):
                for tag in result.get("tags"):
                    if not tag.get("probability"):
                        continue
                    if tag.get("probability") <= self.probability_low or tag.get("probability") >= self.probability_high:
                        self.logger.error(
                            "probability is not in range :[%s,%s] !,see: %s" % (self.probability_low,self.probability_high,item))
                        assert False

        #3，id 是否有重复的,id是否有非int 的
        ids=[]
        for item in r_json.get("succ_results"):
            # self.logger.debug("succ results is  %s " % r_json.get("succ_results"))
            if not isinstance(item.get("id"),int):
                self.logger.error("there has some id not's int : %s" % item)
                assert False
            ids.append(item.get("id"))
        if len(ids) != len(set(ids)):
            self.logger.error("there has some repeat id: real id is %s " % sorted(ids))
            assert False
        # self.logger.debug("id : %s " % set(ids))
        self.logger.info("there are %s id"% len(set(ids)))

        #排序debug
        # self.logger.info("id : %s "% sorted(list(set(ids))))


        #4,id 不能超过5000个
        if len(set(ids)) > 5000:
            self.logger.info("id not greater than 5000,but get %s " % len(set(ids)))
            assert False

        #4，是否key有为空情况存在


        def has_space_key(a):
            if isinstance(a,dict):
                for k,v in a.items():
                    if not len(k.strip()):
                        self.logger.error("there has space key,value is %s " % v)
                        return False
                    if isinstance(v,list):
                        for vv in v :
                            has_space_key(vv)
                    if isinstance(v,dict):
                        has_space_key(v)
            if isinstance(a,list):
                for aa in a:
                    has_space_key(aa)
        # 无return 返回的是none,so 不可以用not None
        if  has_space_key(r_json) is False:
            self.logger.error("the keys has space,pls check %s " %r_json)
            assert False

        #5，shot_results
        #shot_id 不重复,且都是int
        shot_results=r_json.get("shot_results")
        if len(shot_results) == 0:
            self.logger.info("shot_results is []")

        l_a =list()
        if len(shot_results) != 0:
            for x in shot_results:
                if isinstance(x.get("shot_id"),int):
                    l_a.append(x.get("shot_id"))
                else:
                    self.logger.error("shot_id  is not int ,pls check: %s " % x)

        if len(l_a) != len(set(l_a)):
            self.logger.error("there has repeat id ,pls check: %s " % l_a)

            #开始帧id 小于结束帧id,且都是int
            for x in shot_results:
                if isinstance(x.get("start_frame_id"),int) and isinstance(x.get("end_frame_id"),int):
                    if x.get("start_frame_id")>x.get("end_frame_id"):
                        self.logger.error("start_fram_id:%s  must less than end_franme_id :%s !" % (x.get("start_frame_id"),x.get("end_frame_id")))
                        assert False
                else:
                    self.logger.error("start_fram_id:%s and end_franme_id %s must be int  !" % (
                    x.get("start_frame_id"), x.get("end_frame_id")))
                    assert False

        #多个帧区间不重复（[[1,5],[6,9]...] 先排序再前一个的第二个和第二个的第一个元素进行比较）
        list_b=[]
        for x in shot_results:
            list_b.append([x.get("start_frame_id"),x.get("end_frame_id")])
        #排序
        list_b.sort(key=lambda x: x[0])
        # self.logger.info(list_b)

        #判断区间
        for ind in range(len(list_b)-1):
            if list_b[ind][1]>list_b[ind+1][0]:
                self.logger.error("there has repeat qujian ,see: %s,index is %s" %(list_b,ind))
                assert False

        #6，error_results
        if not len(r_json.get("error_results")):
            self.logger.info("error_results is %s " %r_json.get("error_results") )
        else:
            self.logger.error("there have error_results %s " %r_json.get("error_results"))
            assert False



    def teardown(self):
        self.logger.info("test teardown")





"""
{
  "content": [
    {
      "isFinished": 1,
      "updateTime": "2018-12-03T16:21:02.000+0000",
      "createTime": "2018-12-03T16:21:02.000+0000",
      "result": "{\"result_urls\":[\"http://172.20.23.43/sensemedia/video/result/1DpuFyjvhoLy1R9ksaWXCJPpIm3.json\",\"http://172.20.23.43/sensemedia/video/result/1DpuG0QnL1exc0KPartoQOlUNGX.json\"]}",
      "taskId": "afcd13d5-b386-422c-ad99-5da99cef54b7",
      "requestId": "0608aaf4-0fff-48c4-8408-e656bb151c8e",
      "id": 75
    },
    {
      "isFinished": 1,
      "updateTime": "2018-12-03T15:40:11.000+0000",
      "createTime": "2018-12-03T15:40:11.000+0000",
      "result": "image dispatch error",
      "taskId": "afcd13d5-b386-422c-ad99-5da99cef54b7",
      "requestId": "0608aaf4-0fff-48c4-8408-e656bb151c8e",
      "id": 51
    }
  ],
  "size": 2
}

"""