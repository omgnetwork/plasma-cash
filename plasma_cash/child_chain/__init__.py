from flask import Flask

callback = {}


def on(event):
    def decorator(func):
        callback[event] = func
        return func
    return decorator


def emit(event, *arg, **kw):
    if event in callback and callable(callback[event]):
        callback[event](*arg, **kw)


def create_app(is_unit_test=False):
    app = Flask(__name__)

    if not is_unit_test:
        from plasma_cash.dependency_config import container
        # Create a child chain instance when creating a Flask app.
        container.get_child_chain()

    from . import server
    app.register_blueprint(server.bp)

    return app
