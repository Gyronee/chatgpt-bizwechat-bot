import yaml
from tornado.web import Application
import tornado.ioloop
import  tornado.options
from wx_chatbot import WXChatGPTBotHandler, WXChatGPTBot


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    bot = WXChatGPTBot(config.get('wx-bot', dict()), config.get('chatgpt', dict()))

    tornado.options.parse_command_line()

    application = Application([
        (r"/chat", WXChatGPTBotHandler, {"bot": bot})
    ])

    application.listen(8868)

    tornado.ioloop.IOLoop.instance().start()
