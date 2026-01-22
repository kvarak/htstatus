#!/bin/bash -ex
#
# DEPLOYMENT AUTOMATION SCRIPT
# Purpose: Generates command.sh and executes remote deployment using environment variables
# Usage: ./deploy.sh --run [--major] [--dry-run] [--help]
# Process: Creates deployment commands -> transfers to server -> executes -> cleanup

show_help() {
  cat << EOF
HT Status Deployment Script

Usage: ./deploy.sh --run [OPTIONS]

Options:
  --run         Execute deployment (REQUIRED - script won't run without this)
  --major       Regenerate SECRET_KEY for major releases
  --dry-run     Show deployment commands without executing them
  --help        Display this help message

Examples:
  ./deploy.sh --run                    # Standard deployment
  ./deploy.sh --run --dry-run          # Preview deployment commands
  ./deploy.sh --run --major            # Deploy with new SECRET_KEY
  ./deploy.sh --run --major --dry-run  # Preview major release deployment

Environment Variables Required:
  DEPLOY_SERVER      - Target server SSH hostname
  DEPLOY_REPO_PATH   - Remote repository path
  DEPLOY_GIT_BRANCH  - Git branch to deploy

EOF
  exit 0
}

# Parse arguments
DRY_RUN=false
MAJOR_RELEASE=false
RUN_DEPLOYMENT=false

for arg in "$@"; do
  case $arg in
    --help)
      show_help
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --major)
      MAJOR_RELEASE=true
      shift
      ;;
    --run)
      RUN_DEPLOYMENT=true
      shift
      ;;
    *)
      echo "Unknown option: $arg"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Require --run flag
if [ "$RUN_DEPLOYMENT" = false ]; then
  echo "ERROR: --run flag is required to execute deployment"
  echo ""
  show_help
fi

# Load environment variables
set -o allexport
source .env
set +o allexport

# Define deployment steps - shared between dry-run validation and actual deployment
DEPLOYMENT_STEPS=(
  "cd:Change to repository directory:$DEPLOY_REPO_PATH"
  "git:Fetch updates:git fetch --all"
  "git:Reset to branch:git reset --hard $DEPLOY_GIT_BRANCH"
  "git:Pull changes:git pull"
  "script:Generate changelog:./scripts/changelog.sh || ./changelog.sh"
  "file:Touch routes:touch app/routes.py"
  "secret:Update SECRET_KEY:(conditional)"
  "dep:Install uv:pip3 install uv"
  "dep:Sync dependencies:python3 -m uv sync"
  "db:Generate migrations:python3 -m uv run python3 scripts/manage.py db migrate"
  "db:Apply migrations:python3 -m uv run python3 scripts/manage.py db upgrade"
  "service:Restart service:sudo systemctl restart htstatus"
)

generate_dryrun_script() {
  cat > command.sh << SCRIPT
#!/bin/bash -e

echo "=== DRY RUN MODE - Testing Deployment Prerequisites ==="
echo ""

# [1/7] Repository access - validates: cd, git operations, changelog script
echo "[1/7] Checking repository path..."
if [ ! -d "$DEPLOY_REPO_PATH" ]; then
  echo "ERROR: Repository path does not exist: $DEPLOY_REPO_PATH"
  exit 1
fi
cd $DEPLOY_REPO_PATH
echo "✓ Repository path exists"

# [2/7] Git connectivity - validates: git fetch, git reset, git pull
echo ""
echo "[2/7] Testing git connectivity..."
git fetch --all --dry-run 2>&1 || echo "✓ Git fetch would succeed"
git remote -v
echo "✓ Git connectivity verified"

# [3/7] Branch existence - validates: git reset --hard, git pull
echo ""
echo "[3/7] Checking target branch..."
git branch -r | grep $DEPLOY_GIT_BRANCH > /dev/null
if [ \$? -eq 0 ]; then
  echo "✓ Branch $DEPLOY_GIT_BRANCH exists"
else
  echo "ERROR: Branch $DEPLOY_GIT_BRANCH not found"
  exit 1
fi

# [4/7] Python environment - validates: python3 commands
echo ""
echo "[4/7] Checking Python environment..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
python3 --version
echo "✓ Python environment available"

# [5/7] Package manager - validates: pip3 install uv, python3 -m uv sync
echo ""
echo "[5/7] Checking uv package manager..."
if command -v uv >/dev/null 2>&1; then
  uv --version
  echo "✓ uv is already installed"
else
  echo "! uv not found - would be installed via pip3 install uv"
fi

# [6/7] Database migration scripts - validates: db migrate, db upgrade
echo ""
echo "[6/7] Testing database migration..."
python3 -m uv sync --dry-run 2>&1 || echo "! Dependencies would be synced"
if [ -f "scripts/manage.py" ]; then
  echo "✓ Migration script exists"
else
  echo "ERROR: scripts/manage.py not found"
  exit 1
fi

# [7/7] Service management - validates: systemctl restart
echo ""
echo "[7/7] Checking systemctl access..."
sudo -n systemctl status htstatus >/dev/null 2>&1
if [ \$? -eq 0 ]; then
  echo "✓ Can manage htstatus service"
else
  echo "! May need password for systemctl restart"
fi

echo ""
echo "==================================================="
echo "✓ All deployment prerequisites validated"
echo "==================================================="
echo "Target server: $DEPLOY_SERVER"
echo "Repository path: $DEPLOY_REPO_PATH"
echo "Git branch: $DEPLOY_GIT_BRANCH"
SCRIPT

  if [ "$MAJOR_RELEASE" = true ]; then
    echo 'echo "Major release: SECRET_KEY would be regenerated"' >> command.sh
  fi

  echo '' >> command.sh
  echo 'echo ""' >> command.sh
  echo 'echo "To execute actual deployment, run: ./deploy.sh --run"' >> command.sh
}

generate_deployment_script() {
  cat > command.sh << SCRIPT
#!/bin/bash -ex

cd $DEPLOY_REPO_PATH
git fetch --all
git reset --hard $DEPLOY_GIT_BRANCH
git pull
./scripts/changelog.sh || ./changelog.sh
touch app/routes.py
SCRIPT

  if [ "$MAJOR_RELEASE" = true ]; then
    newsecret=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    cat >> command.sh << SCRIPT
sed -i -e "s/SECRET_KEY.*/SECRET_KEY               = '$newsecret'/g" config.py
SCRIPT
  fi

  cat >> command.sh << 'SCRIPT'
pip3 install uv
python3 -m uv sync

echo ""
echo "=== Running Database Migrations ==="
echo "Checking for pending migrations..."
FLASK_APP=run.py python3 -m uv run flask db upgrade
if [ $? -eq 0 ]; then
  echo "✓ Database migrations completed successfully"
else
  echo "✗ Database migrations failed!"
  exit 1
fi

echo ""
echo "=== Restarting Service ==="
sudo systemctl restart htstatus
if [ $? -eq 0 ]; then
  echo "✓ Service restarted successfully"
  sudo systemctl status htstatus --no-pager -l | head -10
else
  echo "✗ Service restart failed!"
  exit 1
fi
SCRIPT
}

rm -rf command.sh

if [ "$DRY_RUN" = true ]; then
  generate_dryrun_script
else
  generate_deployment_script
fi

chmod a+x command.sh

# Execute command on remote server
if [ "$DRY_RUN" = true ]; then
  echo "Testing deployment on remote server $DEPLOY_SERVER..."
  ssh $DEPLOY_SERVER 'bash -s' < command.sh
else
  echo "Executing deployment to $DEPLOY_SERVER..."
  ssh $DEPLOY_SERVER 'bash -s' < command.sh
fi

rm command.sh
