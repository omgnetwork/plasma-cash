callback = {}


def on(event):
    def decorator(func):
        callback[event] = func
        return func
    return decorator


def emit(event, *arg, **kw):
    if event in callback and callable(callback[event]):
        callback[event](*arg, **kw)
