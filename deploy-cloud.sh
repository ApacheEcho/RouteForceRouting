#!/bin/bash
# Cloud Deployment Script for RouteForce

set -e

echo "☁️  RouteForce Cloud Deployment Starting..."
echo "=============================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
ENVIRONMENT="${1:-production}"
NAMESPACE="routeforce"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-routeforce}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Check prerequisites
check_prerequisites() {
    log_info "Checking cloud deployment prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl is not connected to a Kubernetes cluster."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    # Build application image
    log_info "Building application image..."
    docker build -f Dockerfile.production -t ${DOCKER_REGISTRY}/app:${IMAGE_TAG} .
    
    # Push to registry
    log_info "Pushing image to registry..."
    docker push ${DOCKER_REGISTRY}/app:${IMAGE_TAG}
    
    log_success "Images built and pushed successfully"
}

# Create namespace
create_namespace() {
    log_info "Creating Kubernetes namespace..."
    
    if kubectl get namespace ${NAMESPACE} &> /dev/null; then
        log_info "Namespace ${NAMESPACE} already exists"
    else
        kubectl create namespace ${NAMESPACE}
        log_success "Created namespace ${NAMESPACE}"
    fi
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure components..."
    
    kubectl apply -f k8s/01-infrastructure.yaml
    log_success "Infrastructure components deployed"
    
    # Wait for database to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s
    
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=300s
    
    log_success "Infrastructure is ready"
}

# Deploy application
deploy_application() {
    log_info "Deploying application components..."
    
    # Update image tags in deployment
    sed -i.bak "s|routeforce/app:latest|${DOCKER_REGISTRY}/app:${IMAGE_TAG}|g" k8s/02-application.yaml
    
    kubectl apply -f k8s/02-application.yaml
    log_success "Application components deployed"
    
    # Wait for application to be ready
    log_info "Waiting for application to be ready..."
    kubectl wait --for=condition=ready pod -l app=routeforce,component=application -n ${NAMESPACE} --timeout=300s
    
    log_success "Application is ready"
}

# Deploy networking
deploy_networking() {
    log_info "Deploying networking components..."
    
    kubectl apply -f k8s/03-networking.yaml
    log_success "Networking components deployed"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring components..."
    
    kubectl apply -f k8s/04-monitoring.yaml
    log_success "Monitoring components deployed"
    
    # Wait for Prometheus to be ready
    log_info "Waiting for monitoring to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n ${NAMESPACE} --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n ${NAMESPACE} --timeout=300s
    
    log_success "Monitoring is ready"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Get a running app pod
    APP_POD=$(kubectl get pods -n ${NAMESPACE} -l app=routeforce,component=application -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$APP_POD" ]; then
        log_error "No application pods found"
        exit 1
    fi
    
    kubectl exec -n ${NAMESPACE} ${APP_POD} -- flask db upgrade
    log_success "Database migrations completed"
}

# Health checks
perform_health_checks() {
    log_info "Performing health checks..."
    
    # Check application health
    APP_POD=$(kubectl get pods -n ${NAMESPACE} -l app=routeforce,component=application -o jsonpath='{.items[0].metadata.name}')
    
    # Note: app defaults to 8000 in production if PORT is not set.
    # Kubernetes manifests in k8s/ bind service port 5000; ensure the container PORT matches.
    if kubectl exec -n ${NAMESPACE} ${APP_POD} -- curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Application health check passed"
    else
        log_error "Application health check failed"
        return 1
    fi
    
    # Check database connectivity
    if kubectl exec -n ${NAMESPACE} ${APP_POD} -- python -c "from app import create_app; app = create_app(); print('DB OK')" > /dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_warning "Database connectivity check failed (non-critical)"
    fi
}

# Get deployment information
get_deployment_info() {
    echo ""
    echo "🎉 RouteForce Cloud Deployment Complete!"
    echo "========================================"
    echo ""
    
    # Get service information
    log_info "Service Information:"
    kubectl get services -n ${NAMESPACE}
    
    echo ""
    log_info "Pod Status:"
    kubectl get pods -n ${NAMESPACE}
    
    echo ""
    log_info "Ingress Information:"
    kubectl get ingress -n ${NAMESPACE}
    
    echo ""
    log_info "Useful Commands:"
    echo "  • View logs: kubectl logs -f deployment/routeforce-app -n ${NAMESPACE}"
    echo "  • Port forward: kubectl port-forward svc/routeforce-app 8080:5000 -n ${NAMESPACE}  # match service port"
    echo "  • Shell access: kubectl exec -it deployment/routeforce-app -n ${NAMESPACE} -- /bin/bash"
    echo "  • Scale app: kubectl scale deployment routeforce-app --replicas=5 -n ${NAMESPACE}"
    echo ""
    
    # Get external IP if available
    EXTERNAL_IP=$(kubectl get svc routeforce-lb -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
    if [ "$EXTERNAL_IP" != "Pending" ] && [ ! -z "$EXTERNAL_IP" ]; then
        echo "🌐 External Access:"
        echo "  • Application: http://${EXTERNAL_IP}"
        echo "  • Health Check: http://${EXTERNAL_IP}/health"
    else
        echo "⏳ External IP is pending. Check later with:"
        echo "     kubectl get svc routeforce-lb -n ${NAMESPACE}"
    fi
}

# Cleanup on error
cleanup_on_error() {
    log_error "Deployment failed. You can clean up with:"
    echo "  kubectl delete namespace ${NAMESPACE}"
    exit 1
}

# Trap errors
trap cleanup_on_error ERR

# Main deployment flow
main() {
    case $ENVIRONMENT in
        production|staging|development)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT. Use production, staging, or development."
            exit 1
            ;;
    esac
    
    check_prerequisites
    build_and_push_images
    create_namespace
    deploy_infrastructure
    deploy_application
    deploy_networking
    deploy_monitoring
    run_migrations
    perform_health_checks
    get_deployment_info
}

# Run main function
main "$@"
