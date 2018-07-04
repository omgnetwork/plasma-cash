import argparse

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from plasma_cash.child_chain import create_app

if __name__ == '__main__':
    app = create_app()

    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument('--host', default='127.0.0.1', help='Hostname to listen on.')
    parser.add_argument('--port', default='8546', help='Port number to listen on.')
    args = parser.parse_args()

    print('Listening on ' + args.host + ':' + args.port)
    server = pywsgi.WSGIServer((args.host, int(args.port)), app, handler_class=WebSocketHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
