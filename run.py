import os
#import json
#import random

from flask import Flask, request, render_template, session
#from flask_bootstrap import Bootstrap

from authlib.integrations.flask_client import OAuth, OAuthError

app = Flask(__name__)
#bootstrap = Bootstrap(app)


from app import app

#app.secret_key = '!secret'
#app.config.from_object('config')

#oauth = OAuth(app)
#oauth.register(
#    name = 'chpp',
#    api_base_url = 'https://api.twitter.com/1.1/',
#    request_token_url = app.config['RequestTokenPath'],
#    access_token_url = app.config['AccessTokenPath'],
#    authorize_url = app.config['AuthorizePath'],
#    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
#)

# =========================================================================================================

