#!/bin/bash -x

git log 0.2~1..HEAD --oneline --pretty=format:'%cd [%h] - %s' --date=format:'%Y-%m-%d' > app/static/changelog-full.txt

git log 0.2~1..HEAD --oneline --pretty=format:'%cd - %s' --date=format:'%Y-%m-%d' > app/static/changelog.txt

