#!/usr/bin/env python3

"""
File to initalize the AWS Cognito authentor manager.
"""


class CognitoAuthManager(object):
    """
    An object used to hold Flask AWS Cognito settings and callback functions
    for the authentication with AWS Cognito using OAuth2 JWT token.
    Instances of :class:`CognitoAuthManager` are *not* bound to specific apps, so
    you can create one in the main body of your code and then bind it
    to your application.
    Lazy initalization is supported for configuring the application.
    """

    def __init__(self, app=None):
        """
        Create the CognitoAuthManager instance. You can either pass a flask
        application in directly to register the extension with the flask app,
        or call init_app (lazy initalization) after creating the object
        (in a factory pattern).
        :param app: A flask application
        """
        if app is not None:
            self.init(app)
        self.jwt_key = None

    def init(self, app):
        """
        Register this extension with the flask app.
        :param app: A flask application
        """
        # Save this so we can use it later in the extension
        if not hasattr(app, 'extensions'):   # pragma: no cover
            app.extensions = {}
        app.extensions['cognito-flask-auth'] = self
