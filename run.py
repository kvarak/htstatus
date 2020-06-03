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


# =========================================================================================================
