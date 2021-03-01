#!/usr/bin/env python3

"""
File to handle the configurations.
"""

import os
import logging
from flask import current_app
import requests

logger = logging.getLogger(__name__)


class Config(object):
    """
    Helper class to hold the configurations and is meant for internal use
    by module only. This is a loose wrapper for flasks application config
    (alias: `app.config`).
    """

    @property
    def get_auth_manager(self):
        auth_manager = current_app.extensions.get("cognito-flask-auth")
        if not auth_manager:
            msg = "Flask Cognito Auth extention is not registerd with Flask application."
            logger.info(msg)
            raise RuntimeError(msg)

        return auth_manager

    def get_config_value(self, key, error_message, is_key_required, is_value_required):
        if key not in current_app.config and is_key_required:
            raise RuntimeError(error_message)

        value = None
        if key in current_app.config:
            value = current_app.config[key]

        if is_value_required and not value:
            raise RuntimeError(error_message)
        return value

    @property
    def client_id(self):
        error_message = 'COGNITO_CLIENT_ID must be set to validate the audience claim.'
        client_id = self.get_config_value(key="COGNITO_CLIENT_ID",
                                          error_message=error_message,
                                          is_key_required=True,
                                          is_value_required=True)
        return client_id

    @property
    def client_secret(self):
        error_message = 'COGNITO_CLIENT_SECRET must be set to validate the audience claim.'
        client_secret = self.get_config_value(key="COGNITO_CLIENT_SECRET",
                                              error_message=error_message,
                                              is_key_required=True,
                                              is_value_required=True)
        return client_secret

    @property
    def user_pool_id(self):
        error_message = 'COGNITO_USER_POOL_ID must be specified to locate the auth url.'
        pool_id = self.get_config_value(key="COGNITO_USER_POOL_ID",
                                        error_message=error_message,
                                        is_key_required=True,
                                        is_value_required=True)
        return pool_id

    @property
    def domain(self):
        error_message = 'COGNITO_DOMAIN must be set to validate the token redirect to create endpoint url.'
        domain = self.get_config_value(key="COGNITO_DOMAIN",
                                       error_message=error_message,
                                       is_key_required=True,
                                       is_value_required=True)
        if not domain.startswith("https://"):
            domain = f"https://{domain}"
        return domain

    @property
    def region(self):
        error_message = 'COGNITO_REGION must be specified.'
        region = self.get_config_value(key="COGNITO_REGION",
                                       error_message=error_message,
                                       is_key_required=True,
                                       is_value_required=True)
        return region

    @property
    def redirect_uri(self):
        error_message = 'COGNITO_REDIRECT_URI must be set to obtain callback url.'
        uri = self.get_config_value(key="COGNITO_REDIRECT_URI",
                                    error_message=error_message,
                                    is_key_required=True,
                                    is_value_required=True)
        return uri

    @property
    def redirect_error_uri(self):
        uri = self.get_config_value(key="ERROR_REDIRECT_URI",
                                    error_message=None,
                                    is_key_required=False,
                                    is_value_required=False)
        return uri

    @property
    def signout_uri(self):
        error_message = 'COGNITO_SIGNOUT_URI must be set for logout callback.'
        uri = self.get_config_value(key="COGNITO_SIGNOUT_URI",
                                    error_message=error_message,
                                    is_key_required=True,
                                    is_value_required=True)
        return uri

    @property
    def exempt_methods(self):
        methods = self.get_config_value(key="EXEMPT_METHODS",
                                        error_message=None,
                                        is_key_required=False,
                                        is_value_required=False)
        return methods if methods else ["OPTIONS"]

    @property
    def issuer(self):
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"

    @property
    def public_key_uri(self):
        return f"{self.issuer}/.well-known/jwks.json"

    @property
    def jwt_code_exchange_uri(self):
        return f"{self.domain}/oauth2/token"

    @property
    def jwt_cognito_key(self):
        auth_manager = self.get_auth_manager
        # load and cache cognito JSON Web Key (JWK)
        jwt_key = None
        if not auth_manager.jwt_key:
            jwt_key = requests.get(self.public_key_uri).json()["keys"]
        else:
            jwt_key = auth_manager.jwt_key
        return jwt_key

    @property
    def state(self):
        csrf_state = self.get_config_value(key="COGNITO_STATE",
                                           error_message=None,
                                           is_key_required=False,
                                           is_value_required=False)
        return csrf_state

    @property
    def login_uri(self):
        csrf_state = self.state
        state_val = ""
        if csrf_state:
            state_val = f"&state={csrf_state}"
        return (f"{self.domain}/authorize?client_id={self.client_id}"
                f"&response_type=code{state_val}"
                f"&redirect_uri={self.redirect_uri}")

    @property
    def logout_uri(self):
        return (f"{self.domain}/logout?response_type=code"
                f"&client_id={self.client_id}&logout_uri={self.signout_uri}")
