import yaml
from tornado.web import Application
import tornado.ioloop
import  tornado.options
from wx_chatbot import WXChatGPTBotHandler


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        conf = yaml.safe_load(f)

    tornado.options.parse_command_line()

    application = Application([
        (r"/chat", WXChatGPTBotHandler, {"config": conf})
    ])

    application.listen(8868)

    tornado.ioloop.IOLoop.instance().start()
