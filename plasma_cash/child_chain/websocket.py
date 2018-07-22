import json

from .event import emit


def listen(request):
    ws = request.environ['wsgi.websocket']

    try:
        while True:
            data = json.loads(ws.receive())
            if 'event' not in data or 'arg' not in data:
                # Invalid WebSocket request
                continue
            emit('websocket.' + data['event'], ws, data['arg'])
    except TypeError:
        # Ignore disconnection
        pass

    return ws
