from functools import partial
from collections import defaultdict
import logging
from chatbot import ChatBotWithExpiration as ChatBot
from wx_bot import WeChatBot
from tornado.web import RequestHandler
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from tornado.concurrent import run_on_executor
import xml.etree.cElementTree as ET


class WXChatGPTBot(WeChatBot):
    def __init__(self, config: dict, chatgpt_config: dict) -> None:
        super().__init__(config)
        self.chatgpt_config = chatgpt_config
        generate_bot = partial(ChatBot, chatgpt_config)
        self.bot_pool = defaultdict(generate_bot)


class WXChatGPTBotHandler(RequestHandler):

    executor = ThreadPoolExecutor(4)

    def initialize(self, bot: WXChatGPTBot) -> None:
        self.bot = bot

    def get(self):
        msg_signature = self.get_argument("msg_signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")
        ret, echostr = self.bot.wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret !=0 :
            logging.error("[WX-Bot] VerifyURL ret: %s", ret)
        self.write(echostr)

    @gen.coroutine
    def post(self):
        req_signature = self.get_argument("msg_signature")
        req_timestamp = self.get_argument("timestamp")
        req_nonce = self.get_argument("nonce")
        req_data = self.request.body.decode()
        ret, msg = self.bot.wxcpt.DecryptMsg(req_data, req_signature, req_timestamp, req_nonce)
        if ret != 0:
            logging.error("[WX-Bot] Decrypt msg ret: %s", ret)
        try:
            xml_tree = ET.fromstring(msg)
            content = xml_tree.find("Content").text
            user = xml_tree.find("FromUserName").text
            target = xml_tree.find("ToUserName").text
            if target == self.bot.config['CorpID']:
                self.response_user_chat(user, content)
            else:
                raise ValueError("CorpID Mismatch")
        except Exception as e:
            logging.error("[WX-Bot] User request message parse failed: %s, %s", e, xml_tree.text)
        
    @run_on_executor
    def response_user_chat(self, user, content):
        chatbot = self.bot.bot_pool[user]
        if content == '/reset':
            response = chatbot.reset()
        else:
            response = chatbot.get_response(content)
        logging.info("[WX-Bot] Chatbot response for %s: %s", user, response)
        self.bot.send_msg(response, user)
