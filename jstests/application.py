import os
from tornado import web
import tornado.ioloop

from tornadowebapi.registry import Registry
from tornadowebapi.tests.resource_handlers import StudentHandler
from tornadowebapi.tests.resource_handlers import ServerInfoHandler


class Application(web.Application):
    def __init__(self):
        self.reg = Registry()
        self.reg.register(StudentHandler)
        self.reg.register(ServerInfoHandler)
        handlers = self.reg.api_handlers('/')
        base_path = os.path.dirname(os.path.abspath(__file__))
        handlers += [('/(.*)', web.StaticFileHandler, {'path': base_path})]
        print("Serving from base path {}".format(base_path))
        super().__init__(handlers)

    # Public
    def start(self):
        self.listen(12345)
        tornado.ioloop.IOLoop.current().start()


app = Application()
app.start()
