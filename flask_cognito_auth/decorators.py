#!/usr/bin/env python3

"""
File handle the decorators for AWS Cognito login / logout features.
On successfull login, add "groups" in session object if user is
part of AWS Cognito group. This helps application for authorization.
"""

import logging
import json
import requests
from requests.auth import HTTPBasicAuth
from functools import wraps
from flask import redirect
from flask import request
from jose import jwt
from .config import Config
from flask import session
from flask import url_for


logger = logging.getLogger(__name__)
config = Config()


def login_handler(fn):
    """
    A decorator to redirect users to AWS Cognito login if they aren't already.
    If already logged in user will redirect redirect uri.
    Use this decorator on the login endpoint.
    This handle will not return to handle the respose rather redirect to
    redirect uri.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        aws_cognito_login = config.login_uri

        # https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
        res = redirect(aws_cognito_login)
        logger.info("Got Cognito Login, redirecting to AWS Cognito for Auth")
        return res
    return wrapper


def callback_handler(fn):
    """
    A decorator to handle redirects from AWS Cognito login and signup. It
    handles and verifies and exchangs the code for tokens.
    This decorator also pushes the basic informations in Flask session.
    Basic informations are:
        * username
        * group (List of Cognito groups if any)
        * id
        * email
        * expires
        * refresh_token
    Use this decorator on the redirect endpoint on your application.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_success = False
        logger.info("Login is successfull from AWS Cognito.")
        logger.info(
            "Authenticating AWS Cognito application / client, with code exchange.")

        csrf_token = config.state
        csrf_state = None

        if csrf_token:
            csrf_state = request.args.get('state')

        code = request.args.get('code')
        request_parameters = {'grant_type': 'authorization_code',
                              'client_id': config.client_id,
                              'code': code,
                              "redirect_uri": config.redirect_uri}
        response = requests.post(config.jwt_code_exchange_uri,
                                 data=request_parameters,
                                 auth=HTTPBasicAuth(config.client_id,
                                                    config.client_secret))

        # the response:
        # http://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
        if response.status_code == requests.codes.ok:
            logger.info("Code exchange is successfull.")
            logger.info("Validating CSRF state exchange of AWS Cognito")

            if csrf_state == csrf_token:
                auth_success = True

                if csrf_token:
                    logger.info(
                        "CSRF state validation successfull. Login is successfull for AWS Cognito")

                logger.info("Decode the access token from response.")
                verify(response.json()["access_token"])
                id_token = verify(
                    response.json()["id_token"], response.json()["access_token"])

                username = id_token["cognito:username"]
                groups = None
                if "cognito:groups" in id_token:
                    groups = id_token['cognito:groups']

                update_session(username=username,
                               id=id_token["sub"],
                               groups=groups,
                               email=id_token["email"],
                               expires=id_token["exp"],
                               refresh_token=response.json()["refresh_token"])
        if not auth_success:
            error_uri = config.redirect_error_uri
            if error_uri:
                resp = redirect(url_for(error_uri))
                return resp
            else:
                msg = f"Somthing went wrong during authentication"
                return json.dumps({'Error': msg}), 500
        return fn(*args, **kwargs)
    return wrapper


def update_session(username: str, id, groups, email: str, expires, refresh_token):
    """
    Method to update the Flase Session object with the informations after
    successfull login.
    :param username (str):      AWS Cognito authenticated user.
    :param id (str):            ID of AWS Cognito authenticated user.
    :param groups (list):       List of AWS Cognito groups if authenticated
                                user is subscribed.
    :param email (str):         AWS Cognito email if of authenticated user.
    :param expires (str):       AWS Cognito session timeout.
    :param refresh_token (str): JWT refresh token received in respose.
    """
    session['username'] = username
    session['id'] = id
    session['groups'] = groups
    session['email'] = email
    session['expires'] = expires
    session['refresh_token'] = refresh_token


def verify(token: str, access_token: str = None):
    """
    Verifies a JWT string's signature and validates reserved claims.
    Get the key id from the header, locate it in the cognito keys and verify
    the key
    :param token (str):         A signed JWS to be verified.
    :param access_token (str):  An access token string. If the "at_hash" claim
                                is included in the
    :return id_token (dict):    The dict representation of the claims set,
                                assuming the signature is valid and all
                                requested data validation passes.
    """
    header = jwt.get_unverified_header(token)
    key = [k for k in config.jwt_cognito_key if k["kid"] == header['kid']][0]
    id_token = jwt.decode(token,
                          key,
                          audience=config.client_id,
                          access_token=access_token)
    return id_token


def logout_handler(fn):
    """
    A decorator to logout from AWS Cognito and return to signout uri.
    Use this decorator on the cognito logout endpoint.
    This handle will not return to handle any respose rather redirect to
    signout uri.
    This decorator also clears the basic informations from Flask session.
    Basic informations are:
        * username
        * group (List of Cognito groups if any)
        * id
        * email
        * expires
        * refresh_token
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        update_session(username=None,
                       id=None,
                       groups=None,
                       email=None,
                       expires=None,
                       refresh_token=None)
        logger.info(
            "AWS Cognito Login, redirecting to AWS Cognito for logout and terminating sessions")

        aws_cognito_logout = config.logout_uri

        # https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
        res = redirect(aws_cognito_logout)
        return res
    return wrapper
