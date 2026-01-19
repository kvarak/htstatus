#!/bin/bash -ex
#
# DEPLOYMENT AUTOMATION SCRIPT
# Purpose: Generates command.sh and executes remote deployment using environment variables
# Usage: ./push.sh [major] - 'major' flag regenerates SECRET_KEY for major releases
# Process: Creates deployment commands -> transfers to server -> executes -> cleanup

# Load environment variables
set -o allexport
source .env
set +o allexport

rm -rf command.sh

echo '''
#!/bin/bash -ex

cd '"$DEPLOY_REPO_PATH"'
git fetch --all
git reset --hard '"$DEPLOY_GIT_BRANCH"'
git pull
./scripts/changelog.sh || ./changelog.sh
touch app/routes.py
''' >> command.sh
if [ "$1" = "major" ]
then
  newsecret=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
  echo '''
  sed -i -e "s/SECRET_KEY.*/SECRET_KEY               = '\'${newsecret}\''/g" config.py
  ''' >> command.sh
fi
echo '''
pip3 install uv
python3 -m uv sync
python3 -m uv run python3 scripts/manage.py db migrate
python3 -m uv run python3 scripts/manage.py db upgrade
sudo systemctl restart htstatus
''' >> command.sh

chmod a+x command.sh
ssh $DEPLOY_SERVER 'bash -s' < command.sh
rm command.sh
