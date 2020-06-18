#!/bin/bash -x

git log 0.1~1..HEAD --oneline --pretty=format:'%cd %h %s' --date=format:'%Y-%m-%d' > app/static/changelog.txt

