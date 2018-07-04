from flask import Flask
from flask_sockets import Sockets


def create_app(is_unit_test=False):
    app = Flask(__name__)
    sockets = Sockets(app)

    if not is_unit_test:
        from plasma_cash.dependency_config import container
        # Create a child chain instance when creating a Flask app.
        container.get_child_chain()

    from . import server
    app.register_blueprint(server.bp)
    sockets.register_blueprint(server.ws)

    return app
