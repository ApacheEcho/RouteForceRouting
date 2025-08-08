#!/bin/bash

# RouteForce Render Deployment Script
# Comprehensive deployment automation for Render.com platform

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
RENDER_API_BASE="https://api.render.com/v1"

# Default values
ENVIRONMENT="${ENVIRONMENT:-staging}"
DRY_RUN="${DRY_RUN:-false}"
VERBOSE="${VERBOSE:-false}"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

debug() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG] $1${NC}"
    fi
}

# Help function
show_help() {
    cat << EOF
🚀 RouteForce Render Deployment Script

USAGE:
    $0 [OPTIONS] COMMAND

COMMANDS:
    deploy          Deploy to specified environment
    status          Check deployment status
    logs            Fetch deployment logs
    rollback        Rollback to previous version
    health          Run health checks
    setup           Setup Render services
    validate        Validate configuration

OPTIONS:
    -e, --environment ENV    Target environment (staging|production) [default: staging]
    -d, --dry-run           Show what would be done without executing
    -v, --verbose           Enable verbose logging
    -h, --help              Show this help message

ENVIRONMENT VARIABLES:
    RENDER_API_KEY          Render API key (required)
    RENDER_STAGING_SERVICE_ID    Staging service ID
    RENDER_PRODUCTION_SERVICE_ID Production service ID

EXAMPLES:
    $0 deploy --environment staging
    $0 deploy --environment production --dry-run
    $0 status --environment production
    $0 logs --environment staging
    $0 rollback --environment production

EOF
}

# Validation functions
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
        error "Invalid environment: $ENVIRONMENT. Must be 'staging' or 'production'"
        exit 1
    fi
}

validate_api_key() {
    if [[ -z "${RENDER_API_KEY:-}" ]]; then
        error "RENDER_API_KEY environment variable is required"
        exit 1
    fi
}

validate_service_id() {
    local env_upper=$(echo "$ENVIRONMENT" | tr '[:lower:]' '[:upper:]')
    local service_var="RENDER_${env_upper}_SERVICE_ID"
    if [[ -z "${!service_var:-}" ]]; then
        error "$service_var environment variable is required for $ENVIRONMENT deployment"
        exit 1
    fi
}

# API functions
render_api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    local curl_args=(
        -X "$method"
        -H "Authorization: Bearer $RENDER_API_KEY"
        -H "Content-Type: application/json"
        -H "Accept: application/json"
        --max-time 30
        --retry 3
        --retry-delay 2
    )
    
    if [[ -n "$data" ]]; then
        curl_args+=(-d "$data")
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        curl_args+=(--verbose)
    else
        curl_args+=(--silent --show-error)
    fi
    
    debug "API Call: $method $RENDER_API_BASE$endpoint"
    curl "${curl_args[@]}" "$RENDER_API_BASE$endpoint"
}

# Deployment functions
get_service_id() {
    local env_upper=$(echo "$ENVIRONMENT" | tr '[:lower:]' '[:upper:]')
    local service_var="RENDER_${env_upper}_SERVICE_ID"
    echo "${!service_var}"
}

deploy_service() {
    log "🚀 Starting deployment to $ENVIRONMENT environment..."
    
    local service_id=$(get_service_id)
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would deploy service $service_id to $ENVIRONMENT"
        return 0
    fi
    
    # Pre-deployment checks
    run_pre_deployment_checks
    
    # Trigger deployment
    log "📤 Triggering deployment for service: $service_id"
    local deploy_response
    deploy_response=$(render_api_call "POST" "/services/$service_id/deploys" '{"clearCache": "clear"}')
    
    local deploy_id
    deploy_id=$(echo "$deploy_response" | jq -r '.id' 2>/dev/null || echo "unknown")
    
    log "✅ Deployment triggered successfully! Deploy ID: $deploy_id"
    
    # Wait for deployment
    wait_for_deployment "$service_id" "$deploy_id"
    
    # Post-deployment checks
    run_post_deployment_checks
}

wait_for_deployment() {
    local service_id="$1"
    local deploy_id="$2"
    local max_wait=600  # 10 minutes
    local check_interval=15
    local elapsed=0
    
    log "⏳ Waiting for deployment to complete..."
    
    while [[ $elapsed -lt $max_wait ]]; do
        local status_response
        status_response=$(render_api_call "GET" "/services/$service_id/deploys/$deploy_id" || echo '{"status":"unknown"}')
        
        local deploy_status
        deploy_status=$(echo "$status_response" | jq -r '.status' 2>/dev/null || echo "unknown")
        
        case "$deploy_status" in
            "build_in_progress"|"update_in_progress")
                info "🔄 Deployment in progress... (${elapsed}s elapsed)"
                ;;
            "live")
                log "✅ Deployment completed successfully!"
                return 0
                ;;
            "build_failed"|"update_failed"|"deactivated")
                error "❌ Deployment failed with status: $deploy_status"
                fetch_deployment_logs "$service_id"
                exit 1
                ;;
            *)
                warn "⚠️ Unknown deployment status: $deploy_status"
                ;;
        esac
        
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
    done
    
    error "❌ Deployment timed out after ${max_wait}s"
    exit 1
}

run_pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if main branch is up to date
    if command -v git >/dev/null 2>&1; then
        if [[ $(git rev-parse --abbrev-ref HEAD) != "main" ]] && [[ "$ENVIRONMENT" == "production" ]]; then
            warn "⚠️ Not on main branch for production deployment"
        fi
    fi
    
    # Validate Docker configuration
    if [[ -f "$PROJECT_ROOT/Dockerfile.production" ]]; then
        info "✅ Production Dockerfile found"
    else
        error "❌ Production Dockerfile not found"
        exit 1
    fi
    
    # Validate render.yaml
    if [[ -f "$PROJECT_ROOT/render.yaml" ]]; then
        info "✅ Render configuration found"
    else
        error "❌ render.yaml not found"
        exit 1
    fi
    
    log "✅ Pre-deployment checks passed"
}

run_post_deployment_checks() {
    log "🔍 Running post-deployment checks..."
    
    local base_url
    if [[ "$ENVIRONMENT" == "production" ]]; then
        base_url="https://routeforce-routing.onrender.com"
    else
        base_url="https://routeforce-staging.onrender.com"
    fi
    
    # Health check
    log "🏥 Running health check..."
    local health_check_attempts=10
    local health_check_interval=15
    
    for ((i=1; i<=health_check_attempts; i++)); do
        if curl -f -s --max-time 10 "$base_url/health" >/dev/null; then
            log "✅ Health check passed!"
            break
        elif [[ $i -eq $health_check_attempts ]]; then
            error "❌ Health check failed after $health_check_attempts attempts"
            exit 1
        else
            info "⏳ Health check attempt $i/$health_check_attempts failed, retrying..."
            sleep $health_check_interval
        fi
    done
    
    # API smoke tests
    log "🧪 Running API smoke tests..."
    
    local endpoints=(
        "/api/health"
        "/api/routes/test"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s --max-time 10 "$base_url$endpoint" >/dev/null; then
            info "✅ Smoke test passed: $endpoint"
        else
            warn "⚠️ Smoke test failed: $endpoint"
        fi
    done
    
    log "✅ Post-deployment checks completed"
}

get_deployment_status() {
    log "📊 Checking deployment status for $ENVIRONMENT..."
    
    local service_id=$(get_service_id)
    local status_response
    status_response=$(render_api_call "GET" "/services/$service_id")
    
    local service_status
    service_status=$(echo "$status_response" | jq -r '.serviceDetails.status' 2>/dev/null || echo "unknown")
    
    local deploy_status
    deploy_status=$(echo "$status_response" | jq -r '.serviceDetails.deployStatus' 2>/dev/null || echo "unknown")
    
    info "Service Status: $service_status"
    info "Deploy Status: $deploy_status"
    
    if [[ "$service_status" == "available" && "$deploy_status" == "live" ]]; then
        log "✅ Service is healthy and live"
        return 0
    else
        warn "⚠️ Service may have issues"
        return 1
    fi
}

fetch_deployment_logs() {
    local service_id="$1"
    log "📋 Fetching deployment logs..."
    
    local logs_response
    logs_response=$(render_api_call "GET" "/services/$service_id/logs" || echo '{"logs":[]}')
    
    echo "$logs_response" | jq -r '.logs[]?.message // "No logs available"' | tail -50
}

setup_services() {
    log "🛠️ Setting up Render services..."
    
    info "Please ensure the following services are configured in your Render dashboard:"
    echo "1. Web Service: routeforce-app"
    echo "2. PostgreSQL Database: routeforce-postgres"
    echo "3. Redis Cache: routeforce-redis"
    echo "4. Static Site (optional): routeforce-docs"
    echo ""
    echo "Required environment variables:"
    echo "- RENDER_API_KEY"
    echo "- RENDER_STAGING_SERVICE_ID"
    echo "- RENDER_PRODUCTION_SERVICE_ID"
    echo "- Database and Redis connection strings will be auto-generated"
    
    log "✅ Service setup information displayed"
}

rollback_deployment() {
    log "🔄 Rolling back deployment for $ENVIRONMENT..."
    
    local service_id=$(get_service_id)
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would rollback service $service_id"
        return 0
    fi
    
    # Get previous deployment
    local deploys_response
    deploys_response=$(render_api_call "GET" "/services/$service_id/deploys")
    
    local previous_deploy_id
    previous_deploy_id=$(echo "$deploys_response" | jq -r '.[1].id' 2>/dev/null || echo "")
    
    if [[ -z "$previous_deploy_id" || "$previous_deploy_id" == "null" ]]; then
        error "❌ No previous deployment found for rollback"
        exit 1
    fi
    
    log "📤 Rolling back to deployment: $previous_deploy_id"
    render_api_call "POST" "/services/$service_id/deploys" "{\"clearCache\": \"clear\", \"deployId\": \"$previous_deploy_id\"}"
    
    wait_for_deployment "$service_id" "$previous_deploy_id"
    
    log "✅ Rollback completed successfully"
}

validate_config() {
    log "✅ Validating Render configuration..."
    
    # Check render.yaml syntax
    if command -v yq >/dev/null 2>&1; then
        if yq eval . "$PROJECT_ROOT/render.yaml" >/dev/null 2>&1; then
            info "✅ render.yaml syntax is valid"
        else
            error "❌ render.yaml syntax is invalid"
            exit 1
        fi
    else
        warn "⚠️ yq not installed, skipping YAML validation"
    fi
    
    # Check Dockerfile
    if [[ -f "$PROJECT_ROOT/Dockerfile.production" ]]; then
        info "✅ Production Dockerfile exists"
    else
        error "❌ Production Dockerfile missing"
        exit 1
    fi
    
    # Check required environment variables
    validate_api_key
    
    log "✅ Configuration validation completed"
}

# Main execution
main() {
    local command=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            deploy|status|logs|rollback|health|setup|validate)
                command="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate environment
    validate_environment
    
    # Execute command
    case "$command" in
        deploy)
            validate_api_key
            validate_service_id
            deploy_service
            ;;
        status)
            validate_api_key
            validate_service_id
            get_deployment_status
            ;;
        logs)
            validate_api_key
            validate_service_id
            fetch_deployment_logs $(get_service_id)
            ;;
        rollback)
            validate_api_key
            validate_service_id
            rollback_deployment
            ;;
        health)
            run_post_deployment_checks
            ;;
        setup)
            setup_services
            ;;
        validate)
            validate_config
            ;;
        "")
            error "No command specified"
            show_help
            exit 1
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"