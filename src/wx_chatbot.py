import requests
import logging
from revChatGPT.revChatGPT import Chatbot
from collections import defaultdict
from functools import partial
from datetime import datetime
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import yaml
import tornado.ioloop
import tornado.web
from tornado.concurrent import run_on_executor
from tornado import gen


class ChatBotWithExpiration:
    def __init__(self, config) -> None:
        self.bot = Chatbot(config, conversation_id=None)
        self.last_access_time = datetime.now().timestamp()

    def _update_last_access_time(self):
        self.last_access_time = datetime.now().timestamp()

    def reset(self):
        self.bot.reset_chat()
        self._update_last_access_time()

    def get_response(self, text):
        logging.error(f"[WX-BOT] 请求 ChatGPT: {text}")
        response = self.bot.get_chat_response(text)
        self._update_last_access_time()
        return response

class WeChatBot:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.wx_api = {
            "get_token": "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORPID}&corpsecret={SECRET}",
            "send": "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={ACCESS_TOKEN}"
        }
        logging.error("[WX-BOT] 初始化微信机器人")
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
        response = requests.get(url).json()
        logging.error(f"[WX-BOT] 获取 access_token: {response}")
        if response["errcode"] == 0:
            return {
                "access_token": response["access_token"],
                "expire_time": datetime.now().timestamp() + response['expires_in']
            }
        else:
            logging.error(f"请求微信 access_token 失败: {response}")

    def get_token(self):
        if datetime.now().timestamp() >= self.token['expire_time']:
            self._generate_access_token()
        return self.token['access_token']

    def send_msg(self, text, user):
        url = self.wx_api['send'].format(ACCESS_TOKEN=self.get_token())
        logging.error(f"[WX-Bot] 回复 url {url}")
        msg = {
            'touser': f"{user}",
            'msgtype': 'markdown',
            "agentid": self.config["agent_id"],
            "markdown": {
                "content": text
            }
        }
        logging.error(f"[WX-Bot] 回复 {user}: {text}")
        try:
            response = requests.post(url, data=msg)
        except:
            logging.error(f"[WX-Bot] 回传微信消息失败")
            logging.error(f"[WX-Bot] send msg response: {response.json()}")



class ChatGPTWeChatBot(WeChatBot):
    def __init__(self, config: dict, chatgpt_conf: dict) -> None:
        super(ChatGPTWeChatBot, self).__init__(config)
        self.config = config
        self.disallowed_message = "禁止访问的用户"
        self.chatgpt_conf = chatgpt_conf
        generate_bot = partial(ChatBotWithExpiration, chatgpt_conf)
        self.bot_pool = defaultdict(generate_bot)


with open("config.yaml", "r") as f:
    conf = yaml.safe_load(f)

bot = ChatGPTWeChatBot(conf['wx-bot'], conf['chatgpt'])

class ChatbotHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(4)

    def get(self):
        msg_signature = self.get_argument("msg_signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")
        ret, sEchoStr = bot.wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret !=0 :
            logging.error(f"[WX-Bot] ERR: VerifyURL ret: {ret}")
        self.write(sEchoStr)

    @gen.coroutine
    def post(self):
        req_signature = self.get_argument("msg_signature")
        req_timestamp = self.get_argument("timestamp")
        req_nonce = self.get_argument("nonce")
        req_data = self.request.body.decode()
        logging.error(f"req_data")
        ret, sMsg = bot.wxcpt.DecryptMsg(req_data, req_signature, req_timestamp, req_nonce)
        logging.error(f"{ret}\t{sMsg}")
        if ret != 0:
            logging.error(f"[WX-Bot] ERR: decrypt msg ret: {ret}")
        try:
            xml_tree = ET.fromstring(sMsg)
            content = xml_tree.find("Content").text
            user = xml_tree.find("FromUserName").text
        except:
            logging.error(f"[WX-Bot] ERR: 用户请求信息解析失败: {xml_tree.text}")

        self.response_user_chat(user, content)

    @run_on_executor
    def response_user_chat(self, user, content):
        chatbot = bot.bot_pool[user]
        if content == '/reset':
            chatbot.reset()
        else:
            try:
                response = chatbot.get_response(content)
            except:
                logging.error(f"[WX-Bot] ERR: 请求 ChatGPT 失败")
                logging.error(f"[WX-Bot] INFO: ChatGPT- {response}")
            bot.send_msg(response, user)


if __name__ == "__main__":
    application = tornado.web.Application([(r"/chat", ChatbotHandler)])
    application.listen(8868)
    tornado.ioloop.IOLoop.instance().start()
