"""
@Author: NephrenCake
@Date: 2022/5/11
@Desc: 黄金妖精会帮你完成……
"""
import functools
import json
import logging
import sys
import time
import traceback
import requests
import schedule
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import random
from bs4 import BeautifulSoup


def json_to_dict(path):
    with open(path, 'rt', encoding='utf-8') as jsonFile:
        config_dict = json.load(jsonFile)
        return config_dict


def get_logger():
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s : %(message)s"))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(sh)
    return logger


def email_exception(subject="黄金妖精出错", email_notice=True):
    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            self = args[0]
            try:
                res = func(*args, **kwargs)
                return res
            except Exception:
                text = "\n" + traceback.format_exc()
                logging.error(text)
                if email_notice and self.email["sender"] != "":
                    msg = MIMEMultipart()
                    msg.attach(MIMEText(text, 'plain', 'utf-8'))
                    msg['Subject'] = subject
                    msg['From'] = self.email["sender"]
                    s = smtplib.SMTP_SSL(self.email["host"], self.email["port"])
                    s.login(self.email["sender"], self.email["passwd"])
                    s.sendmail(self.email["sender"], self.email["receivers"], msg.as_string())
                    logging.error("邮件已发送")
                return

        return inner

    return wrapper


class GoldenFairy:
    def __init__(self, conf_path="config.json"):
        self.conf = json_to_dict(conf_path)
        self.email = self.conf["email"]
        self.logger = get_logger()

        self.session = requests.Session()

        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-cn',
            'Connection': 'timeout=5',
            "Content-Type": "application/json",
            "User-Agent": "User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
        }

    def login(self, service=None, channelshow=None):
        if service is None:
            service = "https://u.njtech.edu.cn/oauth2/authorize"

        url = f'https://u.njtech.edu.cn/cas/login'
        # 获取i南工登录页面
        response = self.session.get(
            url=url,
            params={
                "service": service
            }
        )

        soup = BeautifulSoup(response.content, "html.parser")
        lt0 = soup.find('input', attrs={'name': 'lt'})['value']
        execution0 = soup.find('input', attrs={'name': 'execution'})['value']
        channel = self.conf["channel"]
        login_info = self.conf["loginInfo"]
        channelshow = login_info["channelshow"] if channelshow is None else channelshow

        # 登录
        response = self.session.post(
            url=url,
            params={
                "service": service
            },
            data={
                'username': login_info['username'],
                'password': login_info['password'],
                'channelshow': channelshow,
                'channel': channel[channelshow],
                'lt': lt0,
                'execution': execution0,
                '_eventId': 'submit',
                'login': '登录',
            },
            allow_redirects=False
        )

        if "Expires" in response.headers.keys():
            self.logger.info(f"成功连接校园网，成功连接[{channelshow}]")

        return response

    def logout(self):
        url = "https://u.njtech.edu.cn/oauth2/logout?redirect_uri=https://i.njtech.edu.cn/index.php/njtech/logout"
        self.session.get(url=url)
        self.session.close()

    @email_exception(subject="健康打卡出错")
    def health(self):
        self.logger.info("开始健康打卡")

        service = "http://pdc.njtech.edu.cn/#/dform/genericForm/wbfjIwyK"
        response = self.login(service=service, channelshow="校园内网")

        # 1. 获取 token
        ticket = response.headers['Location'].split('?ticket=')[-1].split('#/')[0]
        response = self.session.get(
            url=f"http://pdc.njtech.edu.cn/dfi/validateLogin",
            params={
                "ticket": ticket,
                "service": service
            },
            headers=self.headers,
        )
        self.headers["Referer"] = f"http://pdc.njtech.edu.cn/?ticket={ticket}"
        self.headers["Authentication"] = json.loads(response.content)['data']['token']

        # 2. 获取wid
        response = self.session.get(
            "http://pdc.njtech.edu.cn/dfi/formOpen/loadFormListBySUrl",
            params={
                "sUrl": "wbfjIwyK"
            },
            headers=self.headers,
        )
        wid = json.loads(response.content)['data'][0]['WID']

        # 3. 获取最近一次提交数据
        response = self.session.get(
            f"http://pdc.njtech.edu.cn/dfi/formData/loadFormFillHistoryDataList",
            params={
                "formWid": wid,
            },
            headers=self.headers,
        )
        last_data: dict = json.loads(response.content)["data"][0]

        # 4. 发送表单数据
        if 'ONEIMAGEUPLOAD_KWYTQFT3' not in last_data or 'ONEIMAGEUPLOAD_KWYTQFT5' not in last_data:
            self.logger.error("健康码或身份码过期")  # 判断健康码、行程码是否过期

        post_data = {
            "auditConfigWid": "",
            "commitDate": time.strftime("%Y-%m-%d", time.localtime()),
            "commitMonth": time.strftime("%Y-%m", time.localtime()),
            "dataMap": {
                "wid": "",
                "RADIO_KWYTQFSU": "本人知情承诺",  # 知情承诺
                "INPUT_KWYTQFSO": last_data['INPUT_KWYTQFSO'],  # 学号
                "INPUT_KWYTQFSP": last_data['INPUT_KWYTQFSP'],  # 姓名
                "SELECT_KX3ZXSAE": last_data['SELECT_KX3ZXSAE'],  # 学院
                "INPUT_KWYTQFSS": last_data['INPUT_KWYTQFSS'],  # 班级
                "INPUT_KX3ZXSAD": last_data['INPUT_KX3ZXSAD'],  # 手机号
                "INPUT_KWYUM2SI": last_data['INPUT_KWYUM2SI'],  # 辅导员
                "RADIO_KWYTQFSZ": last_data['RADIO_KWYTQFSZ'],  # 当前位置
                "RADIO_KWYTQFT0": last_data['RADIO_KWYTQFT0'],  # 所在省市区
                "CASCADER_KWYTQFT1": last_data['CASCADER_KWYTQFT1'][1:-1].split(', '),
                "RADIO_KWYTQFT2": last_data['RADIO_KWYTQFT2'],  # 身体状况
                "ONEIMAGEUPLOAD_KWYTQFT3": last_data['ONEIMAGEUPLOAD_KWYTQFT3'][1:-1].split(', '),  # 健康码
                "ONEIMAGEUPLOAD_KWYTQFT5": last_data['ONEIMAGEUPLOAD_KWYTQFT5'][1:-1].split(', '),  # 行程码
                "LOCATION_KWYTQFT7": last_data['LOCATION_KWYTQFT7'],  # 定位
            },
            "formWid": wid,
            "userId": "AM@" + str(int(time.time() * 1000)),
        }

        response = self.session.post(
            'http://pdc.njtech.edu.cn/dfi/formData/saveFormSubmitData',
            data=json.dumps(post_data).encode("utf-8"),
            headers=self.headers,
            allow_redirects=False
        )

        response = json.loads(response.content)
        self.logger.info(post_data)
        if response["message"] == "请求成功":
            self.logger.info("健康打卡提交成功！")
        else:
            self.logger.warning("健康打卡提交失败！")
            self.logger.warning(response)
            raise Exception

        # 退出连接
        self.logout()

    @email_exception(subject="图书馆预约出错")
    def library(self, where_to_go="逸夫图书馆"):
        self.logger.info("开始预约图书馆")

        self.login(channelshow="校园内网")

        # 1. get start: 开始事务。获取 token
        start_url = "https://ehall.njtech.edu.cn/infoplus/form/TSGXY/start"
        response = self.session.get(url=start_url)
        soup = BeautifulSoup(response.content, "html.parser")
        token = str(soup.find('meta', attrs={'itemscope': 'csrfToken'})).split('"')[1]

        # 2. post start: 获取 stepId 和 render_url
        self.headers["Referer"] = start_url
        response = self.session.post(
            url="https://ehall.njtech.edu.cn/infoplus/interface/start",
            data=json.dumps({
                "release": "",
                "formData": {"_VAR_URL": start_url, "_VAR_URL_Attr": {}}
            }),
            params={
                "idc": "TSGXY",
                "csrfToken": token,
            },
            headers=self.headers
        )
        render_url: str = json.loads(response.content)["entities"][0]
        step_id = int(render_url.split("/")[-2])

        # 3. post render: 获取个人信息
        self.headers["Referer"] = render_url
        response = self.session.post(
            url="https://ehall.njtech.edu.cn/infoplus/interface/render",
            params={
                "stepId": step_id,
                "csrfToken": token,
            },
            headers=self.headers
        )
        content = json.loads(response.content)
        form_data: dict = content["entities"][0]["data"]
        assign_time = content["entities"][0]["step"]["assignTime"]

        # 4. post listNextStepsUsers: 编辑提交信息，查询是否有空余
        for k, v in form_data.items():
            form_data[k] = str(v)
        form_data["fieldXq_Name"] = where_to_go
        form_data["fieldXq"] = "1" if where_to_go == "逸夫图书馆" else "2"
        form_data["_VAR_ENTRY_NAME"] = "图书馆预约申请"
        form_data["_VAR_ENTRY_TAGS"] = "预约服务"
        form_data["_VAR_RELEASE"] = "true"
        form_data["fieldDateTo"] = int(form_data["_VAR_TODAY"])  # 只能预约当天
        form_data["fieldDateFrom"] = int(form_data["fieldDateFrom"])  # 只能预约当天
        # form_data["fieldJzzt"] = "星期五"  #
        # form_data["fieldKyy"] = "57"  #
        # form_data["fieldYyy"] = "1143"  # 三个废物字段

        response = self.session.post(
            url="https://ehall.njtech.edu.cn/infoplus/interface/listNextStepsUsers",
            params={
                "stepId": step_id,
                "actionId": 1,
                "formData": json.dumps(form_data).encode("utf-8"),
                "timestamp": assign_time,
                "rand": random() * 999,
                "csrfToken": token,
            },
            headers=self.headers,
        )
        response = json.loads(response.content)
        if response["ecode"] == "SUCCEED":
            self.logger.info("还有剩余座位，即将确认预约")
        else:
            self.logger.warning(response)

        # 5. post doAction: 正式提交
        response = self.session.post(
            url="https://ehall.njtech.edu.cn/infoplus/interface/doAction",
            params={
                "stepId": step_id,
                "actionId": 1,
                "formData": json.dumps(form_data).encode("utf-8"),
                "timestamp": assign_time,
                "rand": random() * 999,
                "csrfToken": token,
                "nextUsers": json.dumps({}).encode("utf-8"),
            },
            headers=self.headers,
        )
        response = json.loads(response.content)
        if response["ecode"] == "SUCCEED":
            self.logger.info("还有剩余座位，即将确认预约")
        else:
            self.logger.warning(response)

        # 6. post render: 拿到 instanceId
        response = self.session.post(
            url="https://ehall.njtech.edu.cn/infoplus/interface/render",
            params={
                "stepId": step_id,
                "admin": "false",
                "rand": random() * 999,
                "csrfToken": token,
            },
            headers=self.headers,
        )
        response = json.loads(response.content)
        instance_id = response["entities"][0]["step"]["instanceId"]
        if response["ecode"] == "SUCCEED":
            self.logger.info("成功获取instance_id，即将确认预约")
        else:
            self.logger.warning(response)

        # 7. post progress: 预约
        response = self.session.post(
            url=f"https://ehall.njtech.edu.cn/infoplus/interface/instance/{instance_id}/progress",
            headers=self.headers,
            params={
                "stepId": step_id,
                "includingTop": "true",
                "csrfToken": token,
            },
        )
        response = json.loads(response.content)

        self.logger.info(form_data)
        if response["ecode"] == "SUCCEED":
            self.logger.info(f"{where_to_go}，预约成功")
        else:
            self.logger.warning(response)

        # 退出连接
        self.logout()

    def remote_mission(self):
        schedule.every().day.at("06:01:00").do(self.library)
        schedule.every().day.at("07:00:00").do(self.health)
        while True:
            schedule.run_pending()
            time.sleep(1)

        # nohup python3 -u GoldenFairy.py > output.log 2>&1 &

    def local_mission(self):
        self.login()
        # self.health()
        # self.library("浦江图书馆")


if __name__ == '__main__':
    gf = GoldenFairy()
    # gf.local_mission()
    gf.remote_mission()
