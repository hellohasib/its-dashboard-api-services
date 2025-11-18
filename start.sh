#!/bin/bash
# ATMS System Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_color() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Print header
print_header() {
    echo ""
    print_color "$BLUE" "═══════════════════════════════════════════════════"
    print_color "$BLUE" "  $1"
    print_color "$BLUE" "═══════════════════════════════════════════════════"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    if ! command_exists docker; then
        print_color "$RED" "❌ Docker is not installed. Please install Docker Desktop."
        exit 1
    fi
    print_color "$GREEN" "✓ Docker is installed"
    
    if ! command_exists docker-compose; then
        print_color "$RED" "❌ Docker Compose is not installed."
        exit 1
    fi
    print_color "$GREEN" "✓ Docker Compose is installed"
    
    if ! docker info >/dev/null 2>&1; then
        print_color "$RED" "❌ Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
    print_color "$GREEN" "✓ Docker daemon is running"
}

# Check for .env file
check_env_file() {
    print_header "Checking Environment Configuration"
    
    if [ ! -f .env ]; then
        print_color "$YELLOW" "⚠ .env file not found. Creating from example..."
        
        cat > .env << 'EOF'
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password
DB_ROOT_PASSWORD=rootpassword

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Configuration
SECRET_KEY=dev-secret-key-change-in-production-12345678
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=525600
REFRESH_TOKEN_EXPIRE_DAYS=365

# Application Configuration
APP_ENV=development
DEBUG=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DESTINATION=console

# Observability
OTLP_ENDPOINT=http://otel-collector:4317
LOKI_ENDPOINT=http://loki:3100
LOKI_TIMEOUT_SECONDS=5
LOKI_HTTP_PORT=3100
OTEL_COLLECTOR_GRPC_PORT=4317
OTEL_COLLECTOR_HTTP_PORT=4318

# Frontend API URLs
VITE_API_URL=http://localhost:8001
VITE_ANPR_API_URL=http://localhost:8002
EOF
        
        print_color "$GREEN" "✓ Created .env file with default values"
        print_color "$YELLOW" "  Please review and update .env file if needed"
    else
        print_color "$GREEN" "✓ .env file found"
    fi
}

# Check port availability
check_ports() {
    print_header "Checking Port Availability"
    
    ports=(8001 8002 3307 6379 3100)
    port_names=("Auth+Frontend" "ANPR API" "MySQL" "Redis" "Loki")
    
    for i in "${!ports[@]}"; do
        port=${ports[$i]}
        name=${port_names[$i]}
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_color "$YELLOW" "⚠ Port $port is in use ($name) - may cause conflicts"
        else
            print_color "$GREEN" "✓ Port $port is available ($name)"
        fi
    done
}

# Start services
start_services() {
    print_header "Starting ATMS Services"
    
    MODE=${1:-production}
    
    if [ "$MODE" = "dev" ]; then
        print_color "$BLUE" "Starting in DEVELOPMENT mode with hot reload..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        print_color "$BLUE" "Starting in PRODUCTION mode..."
        docker-compose up -d
    fi
    
    if [ $? -eq 0 ]; then
        print_color "$GREEN" "✓ Services started successfully"
    else
        print_color "$RED" "❌ Failed to start services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_header "Waiting for Services to be Healthy"
    
    print_color "$BLUE" "This may take 2-3 minutes on first startup..."
    echo ""
    
    # Wait for MySQL
    print_color "$YELLOW" "⏳ Waiting for MySQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost --silent >/dev/null 2>&1; then
            print_color "$GREEN" "✓ MySQL is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_color "$YELLOW" "⚠ MySQL health check timed out (may still be starting)"
    fi
    
    # Wait for Redis
    print_color "$YELLOW" "⏳ Waiting for Redis..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
            print_color "$GREEN" "✓ Redis is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    # Wait for services to start
    sleep 5
    
    print_color "$GREEN" "✓ Core services are ready"
}

# Show status
show_status() {
    print_header "Service Status"
    docker-compose ps
}

# Show access information
show_access_info() {
    print_header "Access Information"
    echo ""
    print_color "$GREEN" "🌐 Application (Frontend + Auth API):"
    print_color "$BLUE" "   http://localhost:8001"
    echo ""
    print_color "$GREEN" "📚 API Documentation:"
    print_color "$BLUE" "   Auth API:      http://localhost:8001/docs"
    print_color "$BLUE" "   ANPR API:      http://localhost:8002/docs"
    echo ""
    print_color "$GREEN" "📊 Monitoring:"
    print_color "$BLUE" "   Loki:         http://localhost:3100"
    echo ""
}

# Show helpful commands
show_commands() {
    print_header "Helpful Commands"
    echo ""
    print_color "$YELLOW" "View logs:"
    echo "  docker-compose logs -f"
    echo "  docker-compose logs -f frontend"
    echo ""
    print_color "$YELLOW" "Stop services:"
    echo "  docker-compose down"
    echo ""
    print_color "$YELLOW" "Restart services:"
    echo "  docker-compose restart"
    echo ""
    print_color "$YELLOW" "Rebuild after code changes:"
    echo "  docker-compose up -d --build"
    echo ""
}

# Main function
main() {
    clear
    print_color "$GREEN" ""
    print_color "$GREEN" "  ╔═══════════════════════════════════════════════╗"
    print_color "$GREEN" "  ║                                               ║"
    print_color "$GREEN" "  ║   ATMS - Automated Traffic Management System  ║"
    print_color "$GREEN" "  ║                  Startup Script               ║"
    print_color "$GREEN" "  ║                                               ║"
    print_color "$GREEN" "  ╚═══════════════════════════════════════════════╝"
    print_color "$GREEN" ""
    
    # Parse arguments
    MODE="production"
    if [ "$1" = "dev" ]; then
        MODE="dev"
    fi
    
    # Run checks and start
    check_prerequisites
    check_env_file
    check_ports
    start_services "$MODE"
    wait_for_services
    show_status
    show_access_info
    show_commands
    
    print_header "System Started Successfully! 🚀"
    print_color "$GREEN" "The ATMS system is now running."
    print_color "$BLUE" "Access the application at: http://localhost:8001"
    echo ""
    print_color "$GREEN" "✨ Note: Frontend and Auth API are unified in one container!"
    echo ""
    print_color "$YELLOW" "To view logs, run: docker-compose logs -f"
    print_color "$YELLOW" "To view auth logs: docker-compose logs -f auth-service"
    print_color "$YELLOW" "To stop, run: docker-compose down"
    echo ""
}

# Run main function
main "$@"

