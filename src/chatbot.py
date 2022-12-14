import logging
from datetime import datetime
# from revChatGPT.revChatGPT import Chatbot
from pyChatGPT import ChatGPT


class ChatBotWithExpiration:
    """
    ChatGPTBot with recording last access time
    """
    def __init__(self, config) -> None:
        self.config = config
        self.bot = self._init_bot()
        self.last_access_time = datetime.now().timestamp()
        self.err_msg = "[Chat-Bot] 请求 ChatGPT 失败, 请重试"

    def _init_bot(self) -> ChatGPT:
        try:
            logging.info("[ChatBot] 初始化 Chatbot...")
            # self.bot = Chatbot(config, conversation_id=None)
            bot = ChatGPT(**self.config)
        except Exception as e:
            logging.error("[ChatBot] 初始化 Chatbot 失败: %s", e)
            bot = None
        return bot


    def _update_last_access_time(self):
        self.last_access_time = datetime.now().timestamp()

    def reset(self):
        """
        reset conversation session
        """
        # self.bot.reset_chat()
        self.bot.reset_conversation()
        self._update_last_access_time()
        return "[ChatBot] ChatGPT 会话已重置, 发送消息开始聊天"

    def get_response(self, text):
        """
        request chatgpt and get response
        """
        logging.info("[Chat-Bot] requesting ChatGPT: %s", text)
        try:
            # response = self.bot.get_chat_response(text)["message"]
            if self.bot is None:
                self.bot = self._init_bot()
            response = self.bot.send_message(text)["message"]
        except Exception as e:
            logging.error("[Chat-Bot] Request ChatGPT failed. %s", e)
            response = self.err_msg
        self._update_last_access_time()
        return response
        