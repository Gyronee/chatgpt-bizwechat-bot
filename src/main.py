import yaml
from tornado.web import Application
import tornado.ioloop
from tornado.options import define, options
from wx_chatbot import WXChatGPTBotHandler


if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        conf = yaml.safe_load(f)
    
    define("logging", default="info",
       help=("Set the Python log level. If 'none', tornado won't touch the "
             "logging configuration."),
       metavar="debug|info|warning|error|none")

    application = Application([
        (r"/chat", WXChatGPTBotHandler, {"config": conf})
    ])

    application.listen(8868)

    tornado.ioloop.IOLoop.instance().start()
