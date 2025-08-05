#!/bin/bash
# Branch Protection Setup Script
# This script provides the GitHub CLI commands to set up branch protection rules
# Run this script as a repository administrator

set -e

echo "🔒 Setting up branch protection rules for main branch..."
echo "ℹ️  Note: This script requires GitHub CLI (gh) and admin permissions"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI. Please run 'gh auth login' first."
    exit 1
fi

# Get repository information
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')

echo "📁 Repository: ${REPO_OWNER}/${REPO_NAME}"
echo ""

# Set up branch protection rule for main branch
echo "⚙️  Configuring branch protection rule for 'main' branch..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
  -f required_status_checks='{"strict":true,"contexts":["RouteForce CI/CD Pipeline / test (3.11)","RouteForce CI/CD Pipeline / test (3.12)","RouteForce CI/CD Pipeline / security","RouteForce CI/CD Pipeline / build","Code Quality Checks / lint"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"bypass_pull_request_allowances":{"users":[],"teams":[],"apps":[]}}' \
  -f restrictions=null \
  -f required_linear_history=true \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f block_creations=false \
  -f required_conversation_resolution=true

echo "✅ Branch protection rule configured successfully!"
echo ""

# Verify the configuration
echo "🔍 Verifying branch protection settings..."
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection" \
  --jq '{
    required_status_checks: .required_status_checks,
    enforce_admins: .enforce_admins,
    required_pull_request_reviews: .required_pull_request_reviews,
    restrictions: .restrictions,
    required_linear_history: .required_linear_history,
    allow_force_pushes: .allow_force_pushes,
    allow_deletions: .allow_deletions
  }'

echo ""
echo "🎉 Branch protection setup complete!"
echo ""
echo "📋 Summary of protections applied:"
echo "   ✅ Require pull request reviews (1 approver minimum)"
echo "   ✅ Require code owner reviews"
echo "   ✅ Dismiss stale reviews when new commits are pushed"
echo "   ✅ Require status checks to pass before merging"
echo "   ✅ Require branches to be up to date before merging"
echo "   ✅ Require linear history (no merge commits)"
echo "   ✅ Include administrators in restrictions"
echo "   ✅ Block force pushes"
echo "   ✅ Block branch deletions"
echo "   ✅ Require conversation resolution before merging"
echo ""
echo "📊 Required status checks:"
echo "   - RouteForce CI/CD Pipeline / test (3.11)"
echo "   - RouteForce CI/CD Pipeline / test (3.12)"
echo "   - RouteForce CI/CD Pipeline / security"
echo "   - RouteForce CI/CD Pipeline / build"
echo "   - Code Quality Checks / lint"
echo ""
echo "⚠️  Next steps:"
echo "   1. Test the protection by creating a pull request"
echo "   2. Verify all status checks appear and function correctly"
echo "   3. Confirm review requirements are enforced"
echo "   4. Update team permissions if needed"