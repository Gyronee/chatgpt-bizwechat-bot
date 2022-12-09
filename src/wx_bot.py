import logging
from datetime import datetime
import requests
from WXBizMsgCrypt import WXBizMsgCrypt

class WeChatBot:
    """
    WeChatBot, implement get_token and send message function
    """
    def __init__(self, config: dict) -> None:
        self.config = config
        self.wx_api = {
            "get_token": "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORPID}&corpsecret={SECRET}",
            "send": "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}"
        }
        logging.info("[WX-Bot] Initial WX-Bot")
        self.token = self._generate_access_token()
        self.wxcpt = WXBizMsgCrypt(
            sToken=config['Token'],
            sEncodingAESKey=config['EncodingAESKey'],
            sReceiveId=config['CorpID']
        )

    def _generate_access_token(self):
        url = self.wx_api["get_token"].format(
            CORPID=self.config["CorpID"],
            SECRET=self.config["SECRET"]
        )
        try:
            response = requests.get(url, timeout=5).json()
        except requests.Timeout:
            logging.error("[WX-Bot] Get access_token timeout.")

        logging.info("[WX-Bot] Get access_token: %s", response)
        if response["errcode"] == 0:
            token = {
                "access_token": response["access_token"],
                "expire_time": datetime.now().timestamp() + response['expires_in']
            }
        else:
            logging.error("[WX-Bot] Get access_token failed: %s", response)
            token = dict()
        return token

    def get_token(self):
        if datetime.now().timestamp() >= self.token['expire_time']:
            self.token = self._generate_access_token()
        return self.token['access_token']

    def send_msg(self, text, user):
        url = self.wx_api['send'].format(ACCESS_TOKEN=self.get_token())
        logging.info("[WX-Bot] Reply message to url %s", url)
        msg = {
            'touser': f"{user}",
            'msgtype': 'text',
            "agentid": self.config["agent_id"],
            "text": {
                "content": text
            }
        }
        logging.info("[WX-Bot] Reply %s: %s", user, text)
        try:
            response = requests.post(url, json=msg, timeout=5).json()
            logging.info("[WX-Bot] Response From Wechat server: %s", response)
        except Exception as e:
            logging.error("[WX-Bot] Rely message failed: %s", e)
            response = dict()

        # If Wechat server report access_token expired, try again
        if response.get("errcode") == 42001:
            self.token = self._generate_access_token()
            self.send_msg(text, user)