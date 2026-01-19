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
./changelog.sh
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
source '"$DEPLOY_PYTHON_ENV"'
pip3 install -r requirements.txt
python3 manage.py db migrate
python3 manage.py db upgrade
''' >> command.sh

chmod a+x command.sh
ssh $DEPLOY_SERVER 'bash -s' < command.sh
rm command.sh
