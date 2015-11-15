from app import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


#run server on port 8111
if __name__ == "__main__":
    import click

#    @click.command()
#    @click.option('--debug', is_flag=True)
#    @click.option('--threaded', is_flag=True)
#    @click.argument('HOST', default='0.0.0.0')
#    @click.argument('PORT', default=8111, type=int)
#    def run(debug, threaded, host, port):
#        HOST, PORT = host, port
#        print "running on %s:%d" % (HOST, PORT)
#        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
#
#    run()

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8111)
    IOLoop.instance().start()
