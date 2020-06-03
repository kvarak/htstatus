# HT Status

## Configuration

You need a `config.py` file in the base folder with the following config:

```
import os

class Config(object):
  CONSUMER_KEY             = os.environ.get('CONSUMER_KEY')             or 'you-will-never-guess'
  CONSUMER_SECRETS         = os.environ.get('CONSUMER_SECRETS')         or 'you-will-never-guess'
  REQUEST_TOKEN_PATH       = os.environ.get('REQUEST_TOKEN_PATH')       or 'https://chpp.hattrick.org/oauth/request_token.ashx'
  AUTHORIZE_PATH           = os.environ.get('AUTHORIZE_PATH')           or 'https://chpp.hattrick.org/oauth/authorize.aspx'
  AUTHENTICATE_PATH        = os.environ.get('AUTHENTICATE_PATH')        or 'https://chpp.hattrick.org/oauth/authenticate.aspx'
  ACCESS_TOKEN_PATH        = os.environ.get('ACCESS_TOKEN_PATH')        or 'https://chpp.hattrick.org/oauth/access_token.ashx'
  CHECK_TOKEN_PATH         = os.environ.get('CHECK_TOKEN_PATH')         or 'https://chpp.hattrick.org/oauth/check_token.ashx'
  INVALIDATE_TOKEN_PATH    = os.environ.get('INVALIDATE_TOKEN_PATH')    or 'https://chpp.hattrick.org/oauth/invalidate_token.ashx'
  PROTECTED_RESOURCES_PATH = os.environ.get('PROTECTED_RESOURCES_PATH') or 'https://chpp.hattrick.org/chppxml.ashx'
```
