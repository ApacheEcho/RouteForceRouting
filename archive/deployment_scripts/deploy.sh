#!/bin/bash
# RouteForce Production Deployment Script

set -e

echo "🚀 RouteForce Production Deployment Starting..."
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    log_info "Generating SSL certificates..."
    
    mkdir -p nginx/ssl
    
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
        log_success "SSL certificates generated"
    else
        log_info "SSL certificates already exist"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p logs/nginx
    mkdir -p uploads
    mkdir -p instance
    mkdir -p static/uploads
    
    # Set proper permissions
    chmod 755 logs uploads instance static
    chmod 755 logs/nginx static/uploads
    
    log_success "Directories created"
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.production .env
        log_warning "Created .env file from template. Please update with your production values!"
        log_warning "Important: Change all default passwords and API keys!"
    else
        log_info "Environment file already exists"
    fi
}

# Build and start services
deploy_services() {
    log_info "Building and deploying services..."
    
    # Pull latest images
    docker-compose -f docker-compose.production.yml pull
    
    # Build application image
    docker-compose -f docker-compose.production.yml build --no-cache app
    
    # Start all services
    docker-compose -f docker-compose.production.yml up -d
    
    log_success "Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    until docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U routeforce -d routeforce; do
        sleep 2
    done
    log_success "PostgreSQL is ready"
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    until docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping; do
        sleep 2
    done
    log_success "Redis is ready"
    
    # Wait for application
    log_info "Waiting for application..."
    sleep 10
    until curl -f http://localhost/health > /dev/null 2>&1; do
        sleep 5
    done
    log_success "Application is ready"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose -f docker-compose.production.yml exec app flask db upgrade
    
    log_success "Database migrations completed"
}

# Health checks
perform_health_checks() {
    log_info "Performing health checks..."
    
    # Check application health
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Application health check passed"
    else
        log_error "Application health check failed"
        return 1
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        log_success "Prometheus health check passed"
    else
        log_warning "Prometheus health check failed (non-critical)"
    fi
    
    # Check Grafana
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        log_success "Grafana health check passed"
    else
        log_warning "Grafana health check failed (non-critical)"
    fi
}

# Display deployment info
show_deployment_info() {
    echo ""
    echo "🎉 RouteForce Production Deployment Complete!"
    echo "=============================================="
    echo ""
    echo "📊 Service URLs:"
    echo "  • Application:  https://localhost"
    echo "  • Health Check: http://localhost/health"
    echo "  • Metrics:      http://localhost/metrics"
    echo "  • Prometheus:   http://localhost:9090"
    echo "  • Grafana:      http://localhost:3000"
    echo ""
    echo "🔐 Default Credentials:"
    echo "  • Grafana: admin / admin_secure_2024"
    echo ""
    echo "⚠️  Security Reminders:"
    echo "  • Update all default passwords in .env file"
    echo "  • Replace self-signed SSL certificates with real ones"
    echo "  • Configure firewall rules for production"
    echo "  • Set up backup procedures"
    echo ""
    echo "📖 Useful Commands:"
    echo "  • View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "  • Stop services: docker-compose -f docker-compose.production.yml down"
    echo "  • Restart: docker-compose -f docker-compose.production.yml restart"
    echo ""
}

# Cleanup on error
cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    docker-compose -f docker-compose.production.yml down
    exit 1
}

# Trap errors
trap cleanup_on_error ERR

# Main deployment flow
main() {
    check_prerequisites
    generate_ssl_certs
    create_directories
    setup_environment
    deploy_services
    wait_for_services
    run_migrations
    perform_health_checks
    show_deployment_info
}

# Run main function
main "$@"
