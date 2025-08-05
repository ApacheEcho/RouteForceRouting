#!/bin/bash

# Release Helper Script for RouteForce Routing
# This script helps create new releases with proper versioning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
Release Helper Script for RouteForce Routing

Usage: $0 [OPTIONS] VERSION

This script helps create new releases with proper versioning and changelog updates.

VERSION FORMAT:
  - MAJOR.MINOR.PATCH (e.g., 1.0.0)
  - MAJOR.MINOR.PATCH-PRERELEASE (e.g., 1.0.0-beta.1)

OPTIONS:
  -h, --help     Show this help message
  -d, --dry-run  Show what would be done without making changes
  -f, --force    Skip confirmation prompts

EXAMPLES:
  $0 1.0.0                  # Create release v1.0.0
  $0 1.1.0-beta.1          # Create pre-release v1.1.0-beta.1
  $0 --dry-run 2.0.0       # Preview what would happen for v2.0.0
  $0 --force 1.0.1         # Create release without confirmation

WORKFLOW:
  1. Validates version format
  2. Updates VERSION file
  3. Creates git tag
  4. Pushes tag to trigger release automation
  5. Opens the releases page

EOF
}

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

log_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

# Validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
        log_error "Invalid version format: $version"
        log_info "Expected format: MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-PRERELEASE"
        log_info "Examples: 1.0.0, 1.2.3-beta.1, 2.0.0-rc.1"
        exit 1
    fi
}

# Check if tag already exists
check_tag_exists() {
    local tag="v$1"
    if git tag --list | grep -q "^$tag$"; then
        log_error "Tag $tag already exists!"
        log_info "Existing tags:"
        git tag --list | sort -V | tail -5
        exit 1
    fi
}

# Get current version
get_current_version() {
    if [ -f "$PROJECT_DIR/VERSION" ]; then
        cat "$PROJECT_DIR/VERSION"
    else
        echo "0.0.0"
    fi
}

# Compare versions
version_greater_than() {
    printf '%s\n%s\n' "$2" "$1" | sort -V | head -n1 | grep -q "^$2$"
}

# Update version file
update_version_file() {
    local version=$1
    echo "$version" > "$PROJECT_DIR/VERSION"
    log_success "Updated VERSION file to $version"
}

# Create and push tag
create_and_push_tag() {
    local version=$1
    local tag="v$version"
    
    # Stage VERSION file
    git add "$PROJECT_DIR/VERSION"
    
    # Check if there are any changes to commit
    if git diff --staged --quiet; then
        log_info "No changes to commit"
    else
        git commit -m "Bump version to $version"
        log_success "Committed version bump"
    fi
    
    # Create annotated tag
    git tag -a "$tag" -m "Release $tag"
    log_success "Created tag $tag"
    
    # Push tag to origin
    git push origin "$tag"
    log_success "Pushed tag $tag to origin"
    
    # Also push the version commit if it was created
    if ! git diff --quiet HEAD~1 HEAD; then
        git push origin
        log_success "Pushed version commit"
    fi
}

# Main function
main() {
    local dry_run=false
    local force=false
    local version=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dry-run)
                dry_run=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                version="$1"
                shift
                ;;
        esac
    done
    
    # Check if version is provided
    if [ -z "$version" ]; then
        log_error "Version is required"
        show_help
        exit 1
    fi
    
    # Validate version format
    validate_version "$version"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "There are uncommitted changes in the repository"
        if [ "$force" = false ]; then
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Aborted"
                exit 1
            fi
        fi
    fi
    
    # Check if tag already exists
    check_tag_exists "$version"
    
    # Get current version for comparison
    current_version=$(get_current_version)
    log_info "Current version: $current_version"
    log_info "New version: $version"
    
    # Validate version progression (warning only)
    if [ "$current_version" != "0.0.0" ] && ! version_greater_than "$version" "$current_version"; then
        log_warning "New version ($version) is not greater than current version ($current_version)"
        if [ "$force" = false ]; then
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Aborted"
                exit 1
            fi
        fi
    fi
    
    # Show what will be done
    echo
    log_info "Release Plan:"
    echo "  📝 Update VERSION file: $current_version → $version"
    echo "  🏷️  Create git tag: v$version"
    echo "  🚀 Push tag to trigger release automation"
    echo "  📦 GitHub will automatically:"
    echo "     - Run tests"
    echo "     - Build release assets"
    echo "     - Generate changelog"
    echo "     - Create GitHub release"
    echo
    
    if [ "$dry_run" = true ]; then
        log_info "Dry run mode - no changes will be made"
        exit 0
    fi
    
    # Confirm before proceeding
    if [ "$force" = false ]; then
        read -p "Proceed with release? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Aborted"
            exit 1
        fi
    fi
    
    # Execute the release
    log_info "Creating release v$version..."
    
    update_version_file "$version"
    create_and_push_tag "$version"
    
    echo
    log_success "Release v$version initiated successfully!"
    log_info "🔗 Monitor progress at: https://github.com/ApacheEcho/RouteForceRouting/actions"
    log_info "🎉 Release will be available at: https://github.com/ApacheEcho/RouteForceRouting/releases/tag/v$version"
    
    # Optionally open the releases page
    if command -v xdg-open > /dev/null 2>&1; then
        log_info "Opening releases page..."
        xdg-open "https://github.com/ApacheEcho/RouteForceRouting/releases" 2>/dev/null || true
    elif command -v open > /dev/null 2>&1; then
        log_info "Opening releases page..."
        open "https://github.com/ApacheEcho/RouteForceRouting/releases" 2>/dev/null || true
    fi
}

# Run main function
main "$@"