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

### SQLAlchemy

*Create*
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
*Upgrade*
```
python manage.py db migrate
python manage.py db upgrade
```
*On problems*
```
python manage.py db stamp head
```

### Postgres

*Create*
```
CREATE DATABASE htplanner;
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
pipreqs . --force
pip install -r requirements.txt
```

## Start
```
nohup ./run.sh 5000 &
```
