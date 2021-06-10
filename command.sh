
#!/bin/bash -ex

cd ~/repos/htstatus
git fetch --all
git reset --hard origin/master
git pull
./changelog.sh
touch app/routes.py


pip3 install -r requirements.txt
python3 manage.py db migrate
python3 manage.py db upgrade

