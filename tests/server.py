import pytest
from flask import Flask
from flask_cognito_auth import CognitoAuthManager


@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    _ = CognitoAuthManager(app)
    app.secret_key = "my super secret key"
    return app


@pytest.fixture(scope='function')
def app_exception():
    app = Flask(__name__)
    _ = CognitoAuthManager()
    return app


@pytest.fixture(scope='function')
def app_lazy():
    app = Flask(__name__)
    cognito_auth_manager = CognitoAuthManager()
    cognito_auth_manager.init(app)
    return app
