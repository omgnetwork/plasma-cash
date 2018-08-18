from flask import Flask


def create_app(is_unit_test=False):
    app = Flask(__name__)

    if not is_unit_test:
        from plasma_cash.dependency_config import container
        # Create a child chain instance when creating a Flask app.
        container.get_child_chain()

    from . import server
    app.register_blueprint(server.api)
    app.register_blueprint(server.operator, url_prefix='/operator')

    return app
