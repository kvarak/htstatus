#!/usr/bin/python3

import platform
from flask import Flask

# --------------------------------------------------------------------------------

print("Python version " + platform.python_version())

app = Flask(__name__)

from app import app
