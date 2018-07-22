import json

callback = {}


def on(event):
    def decorator(func):
        callback[event] = func
        return func
    return decorator


def listen(request):
    ws = request.environ['wsgi.websocket']

    try:
        while True:
            data = json.loads(ws.receive())
            if 'event' not in data or 'arg' not in data or data['event'] not in callback:
                # Invalid WebSocket request
                continue
            callback[data['event']](ws, data['arg'])
    except TypeError:
        # Ignore disconnection
        pass

    return ws
