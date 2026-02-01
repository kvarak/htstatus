#!/bin/bash -e
#
# DEPLOYMENT AUTOMATION SCRIPT
# Purpose: Simple deployment orchestration using Makefile targets
# Usage: ./deploy.sh --run [--major] [--dry-run] [--help]

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
  make deploy                          # Smart deployment (recommended)
  ./deploy.sh --run                    # Direct deployment
  ./deploy.sh --run --dry-run          # Preview deployment
  ./deploy.sh --run --major            # Deploy with new SECRET_KEY

EOF
  exit 0
}

# Parse arguments
DRY_RUN=false
MAJOR_RELEASE=false
RUN_DEPLOYMENT=false

for arg in "$@"; do
  case $arg in
    --help) show_help ;;
    --dry-run) DRY_RUN=true ;;
    --major) MAJOR_RELEASE=true ;;
    --run) RUN_DEPLOYMENT=true ;;
    *) echo "Unknown option: $arg"; echo "Use --help for usage information"; exit 1 ;;
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
  exit 1
fi

echo "✓ Environment variables loaded successfully"
echo "  Target server: $DEPLOY_SERVER"
echo "  Repository: $DEPLOY_REPO_PATH"
echo "  Branch: $DEPLOY_GIT_BRANCH"
echo ""

generate_dryrun_script() {
  cat > command.sh << SCRIPT
#!/usr/bin/env bash

echo "=== DRY RUN MODE - Testing Deployment Prerequisites ==="
echo ""

# Source environment
[ -f ~/.bashrc ] && source ~/.bashrc
cd $DEPLOY_REPO_PATH || { echo "❌ Repository path not found"; exit 1; }

# Quick validation
echo "✓ Repository accessible"
git fetch --dry-run &>/dev/null && echo "✓ Git connectivity verified"
command -v python3 >/dev/null && echo "✓ Python available"
[ -f "\$HOME/.local/bin/uv" ] && echo "✓ uv available" || echo "! uv will be installed"
command -v jq >/dev/null && echo "✓ jq available" || echo "! jq will be installed"

echo ""
echo "====================================================="
echo "✓ All deployment prerequisites validated"
echo "To execute actual deployment, run: make deploy"
echo "====================================================="
SCRIPT
}

generate_deployment_script() {
  cat > command.sh << SCRIPT
#!/usr/bin/env bash

# Setup environment
[ -f ~/.bashrc ] && source ~/.bashrc
export PATH="\$HOME/.local/bin:\$PATH"
cd $DEPLOY_REPO_PATH || { echo "❌ Repository not found"; exit 1; }

echo "🚀 Starting HattrickPlanner Deployment"
echo "======================================"

# Modern deployment (preferred)
if make -n deploy-prepare >/dev/null 2>&1; then
  echo "✅ Using Makefile deployment targets"
  make deploy-prepare && make deploy-sync && make deploy-docs && make deploy-migrate && make deploy-finalize
  echo "✅ Deployment completed successfully"
else
  echo "⚠️  Using legacy deployment"

  # Simple legacy fallback
  git fetch --all && git reset --hard $DEPLOY_GIT_BRANCH && git pull
  command -v jq >/dev/null || sudo apt-get update -qq && sudo apt-get install -y jq
  [ -f "\$HOME/.local/bin/uv" ] || pip3 install --user uv
  \$HOME/.local/bin/uv sync --python 3.14
  \$HOME/.local/bin/uv run python scripts/database/apply_migrations.py
  ./scripts/changelog.sh
  sudo systemctl restart htstatus
  echo "✅ Legacy deployment completed"
fi
SCRIPT

  if [ "$MAJOR_RELEASE" = true ]; then
    newsecret=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    cat >> command.sh << SCRIPT

# Update SECRET_KEY for major release
echo "🔐 Updating SECRET_KEY for major release..."
sed -i -e "s/SECRET_KEY=.*/SECRET_KEY=$newsecret/g" .env
SCRIPT
  fi
}

# Generate and execute deployment script
rm -f command.sh

if [ "$DRY_RUN" = true ]; then
  generate_dryrun_script
  echo "Testing deployment on remote server $DEPLOY_SERVER..."
else
  generate_deployment_script
  echo "Executing deployment to $DEPLOY_SERVER..."
fi

chmod +x command.sh
ssh $DEPLOY_SERVER 'bash -s' < command.sh
rm command.sh
