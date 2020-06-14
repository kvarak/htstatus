# HT Status

## Configuration

You need a `config.py` file in the base folder with the following config:

```
import os

class Config(object):
  APP_NAME                 = 'your-app-name'
  SECRET_KEY               = 'you-will-never-guess'
  CONSUMER_KEY             = 'you-will-never-guess'
  CONSUMER_SECRETS         = 'you-will-never-guess'
  CALLBACK_URL             = 'url-to-your-callback'
  CHPP_URL                 = 'https://chpp.hattrick.org/chppxml.ashx'
  SQLALCHEMY_DATABASE_URI  = 'postgresql:///<dbname>'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Database

### Postgres

*Create (and upgrade)*
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
*Check*
```
$ psql
# \c htplanner
# \dt
# \d results
```

## Requirements

- Postgres
- Python 3+
- Flask
- flask_script

### Manage requirements
```
python -m pip freeze > requirements.txt
pip install -r requirements.txt
```
