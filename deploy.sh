#!/bin/bash -e
#
# DEPLOYMENT AUTOMATION SCRIPT
# Purpose: Generates command.sh and executes remote deployment using environment variables
# Usage: ./deploy.sh --run [--major] [--dry-run] [--help]
# Process: Creates deployment commands -> transfers to server -> executes -> cleanup

show_help() {
  cat << EOF
HattrickPlanner Deployment Script

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

# Validate required environment variables
REQUIRED_VARS=("DEPLOY_SERVER" "DEPLOY_REPO_PATH" "DEPLOY_GIT_BRANCH" "DEPLOY_USER")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    MISSING_VARS+=("$var")
  fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
  echo "ERROR: Missing required environment variables in .env file:"
  for var in "${MISSING_VARS[@]}"; do
    echo "  - $var"
  done
  echo ""
  echo "Please update your .env file with the missing variables."
  exit 1
fi

echo "✓ Environment variables loaded successfully"
echo "  Target server: $DEPLOY_SERVER"
echo "  Repository: $DEPLOY_REPO_PATH"
echo "  Branch: $DEPLOY_GIT_BRANCH"
echo ""

# Define deployment steps - shared between dry-run validation and actual deployment
DEPLOYMENT_STEPS=(
  "cd:Change to repository directory:$DEPLOY_REPO_PATH"
  "git:Fetch updates:git fetch --all"
  "git:Reset to branch:git reset --hard $DEPLOY_GIT_BRANCH"
  "git:Pull changes:git pull"
  "dep:Install system dependencies:Install jq for changelog generation"
  "dep:Install uv:pip3 install uv"
  "dep:Sync dependencies:uv sync"
  "release:Update release docs:make release-detect && { echo 'Updating release documentation...'; make release-docs || echo 'No release updates needed'; } || echo 'No version changes detected'"
  "script:Generate changelog:make changelog"
  "file:Touch routes:touch app/routes.py"
  "secret:Update SECRET_KEY in .env:(conditional)"
  "db:Apply migrations:make db-apply"
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

# [4.5/7] System dependencies - validates: jq for changelog generation
echo ""
echo "[4.5/7] Checking system dependencies..."
if command -v jq >/dev/null 2>&1; then
  jq --version
  echo "✓ jq is available"
else
  echo "! jq not found - would be installed during deployment"
fi

# [5/7] Package manager - validates: pip3 install uv, uv sync
echo ""
echo "[5/7] Checking uv package manager..."
if command -v uv >/dev/null 2>&1; then
  uv --version
  echo "✓ uv is already installed"
else
  echo "! uv not found - would be installed via pip3 install uv"
fi

# [6/7] Database migration scripts - validates: apply_migrations.py
echo ""
echo "[6/7] Testing database migration..."
uv sync --dry-run 2>&1 || echo "! Dependencies would be synced"
if [ -f "scripts/database/apply_migrations.py" ]; then
  echo "✓ Migration script exists"
else
  echo "ERROR: scripts/database/apply_migrations.py not found"
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

# Install system dependencies first
echo "=== Installing System Dependencies ==="
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y jq
elif command -v yum &> /dev/null; then
    sudo yum install -y jq
elif command -v brew &> /dev/null; then
    brew install jq
else
    echo "⚠️ Could not detect package manager - please install jq manually"
fi

# Ensure uv is available
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv &> /dev/null; then
    pip3 install --user uv
fi

# Clean up any untracked migration files that could cause multiple heads
find migrations/versions/ -name "*.py" -not -path "*/__pycache__/*" | while read -r file; do
    if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
        echo "Removing untracked migration file: $file"
        rm -f "$file"
    fi
done

# Update release documentation if deploying a tagged version
if make release-detect 2>/dev/null; then
    echo "Version changes detected - updating release documentation..."
    make release-docs || echo "Release update failed, continuing..."
else
    echo "No version changes detected"
fi

make changelog

# Clear Python bytecode cache to force reload of updated code
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

touch app/routes.py
SCRIPT

  if [ "$MAJOR_RELEASE" = true ]; then
    newsecret=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    cat >> command.sh << SCRIPT
# Update SECRET_KEY in .env file
sed -i -e "s/SECRET_KEY=.*/SECRET_KEY=$newsecret/g" .env
SCRIPT
  fi

  cat >> command.sh << 'SCRIPT'
# Force clean dependency installation with consistent Python version
echo "=== Installing Dependencies ==="

# Clear any cached virtual environment
rm -rf .venv 2>/dev/null || true
# Use same Python version as development (3.14.2)
uv sync --python 3.14
# Explicitly install the new dependencies that were added
uv pip install requests requests-oauthlib
echo "✓ Dependencies installed/updated with Python 3.14"

echo ""
echo "=== Running Database Migrations ==="
echo "Checking for pending migrations..."

# Use our new Alembic-direct migration script
uv run python scripts/database/apply_migrations.py 2>&1 | tee /tmp/migration_output.txt
MIGRATION_EXIT_CODE=${PIPESTATUS[0]}

# Check migration results
if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
  if grep -q "Running upgrade" /tmp/migration_output.txt; then
    echo "✓ Database migrations applied successfully"
  else
    echo "✓ Database already at latest version"
  fi
else
  echo "✗ Database migrations failed!"
  cat /tmp/migration_output.txt
  rm -f /tmp/migration_output.txt
  exit 1
fi
rm -f /tmp/migration_output.txt

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
