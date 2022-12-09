import logging
from datetime import datetime
from revChatGPT.revChatGPT import Chatbot


class ChatBotWithExpiration:
    """
    ChatGPTBot with recording last access time
    """
    def __init__(self, config) -> None:
        self.bot = Chatbot(config, conversation_id=None)
        self.last_access_time = datetime.now().timestamp()
        self.err_msg = "[Chat-Bot] Request ChatGPT failed, please try again"

    def _update_last_access_time(self):
        self.last_access_time = datetime.now().timestamp()

    def reset(self):
        """
        reset conversation session
        """
        self.bot.reset_chat()
        self._update_last_access_time()
        return "[ChatBot] ChatGPT 会话已重置, 发送消息开始聊天"

    def get_response(self, text):
        """
        request chatgpt and get response
        """
        logging.info("[Chat-Bot] requesting ChatGPT: %s", text)
        try:
            response = self.bot.get_chat_response(text)["message"]
        except Exception as e:
            logging.error("[Chat-Bot] Request ChatGPT failed. %s", e)
            response = self.err_msg
        self._update_last_access_time()
        return response
        