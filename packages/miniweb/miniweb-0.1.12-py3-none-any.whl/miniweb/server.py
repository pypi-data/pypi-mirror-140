
import logging

from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIServer
from wsgiref.simple_server import WSGIRequestHandler
from http.server import ThreadingHTTPServer


logger = logging.getLogger(__name__)

class _ThreadingWSGIServer(WSGIServer, ThreadingHTTPServer):
    pass

class ThreadingWSGIServer(object):
    def __init__(self, application, listen="127.0.0.1", port=8000, handler_class=WSGIRequestHandler, pre_serve_callback=None) -> None:
        self.application = application
        self.listen = listen
        self.port = port
        self.handler_class = handler_class
        self.httpd = None
        self.pre_serve_callback = pre_serve_callback

    def serve_forever(self):
        with make_server(
                self.listen,
                self.port,
                self.application,
                server_class=_ThreadingWSGIServer,
                handler_class=self.handler_class,
                ) as httpd:
            logger.info("Starting ThreadingWSGIServer at http://{0}:{1}".format(self.listen, self.port))
            self.httpd = httpd
            if self.pre_serve_callback:
                self.pre_serve_callback()
            httpd.serve_forever()
    
    def shutdown(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd = None

    start = serve_forever # alias for serve_forever
    stop = shutdown # alias for shutdown
