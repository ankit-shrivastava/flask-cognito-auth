import pytest
from flask import Flask
from flask_cognito_auth import CognitoAuthManager


@pytest.fixture(scope='function')
def app():
    app = Flask(__name__)
    cognito_auth_manager = CognitoAuthManager()
    cognito_auth_manager.init(app)
    return app
