#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@time   : 2020/8/21 16:04
@file   : drobot.py
@author :
@desc   : 此脚本是用py3执行
@exec   :
"""
import json
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse


class SendMessage():
    def __init__(self, secret, token):
        self.token = token
        self.secret = secret

    def ding_sign(self):
        """
        钉钉安全：加签
        :return:
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def send_message(self, msg_style):
        """
        传入消息格式及内容
        :param msg_style:  消息格式
        :return:
        """
        ts, sign = self.ding_sign()
        url = 'https://oapi.dingtalk.com/robot/send?access_token={token}&timestamp={time}&sign={sign}' \
            .format(token=self.token, time=ts, sign=sign)

        pagrem = msg_style

        headers = {
            'Content-Type': 'application/json'
        }
        requests.post(url, data=json.dumps(pagrem), headers=headers)

    def style_actioncard(self, btns, title, content, atone="", isatall=False):
        pagrem = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": content,
                "btnOrientation": "0",
                "btns": btns
            },
            "at": {
                "atMobiles": [
                    atone  # 需要填写自己的手机号，钉钉通过手机号@对应人
                ],
                "isAtAll": isatall  # 是否@所有人，默认否
            }
        }
        return pagrem

    def style_text(self, content, atone="", isatall=False):
        pagrem = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": [
                    atone
                ],
                "isAtAll": isatall
            }
        }
        return pagrem

    def style_md(self, title, content, atone="", isatall=False):
        """
        :param title:
        :param content:
        :param atone:
        :param isatall:
        :return:
        """
        pagrem = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            },
            "at": {
                "atMobiles": [
                    atone
                ],
                "isAtAll": isatall
            }
        }
        return pagrem
