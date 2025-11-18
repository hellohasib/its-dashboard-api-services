#!/bin/bash
# ATMS System Stop Script

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

main() {
    clear
    print_color "$YELLOW" ""
    print_color "$YELLOW" "  ╔═══════════════════════════════════════════════╗"
    print_color "$YELLOW" "  ║                                               ║"
    print_color "$YELLOW" "  ║   ATMS - Automated Traffic Management System  ║"
    print_color "$YELLOW" "  ║                  Stop Script                  ║"
    print_color "$YELLOW" "  ║                                               ║"
    print_color "$YELLOW" "  ╚═══════════════════════════════════════════════╝"
    print_color "$YELLOW" ""
    
    print_header "Stopping ATMS Services"
    
    # Parse arguments
    REMOVE_VOLUMES=false
    if [ "$1" = "--clean" ] || [ "$1" = "-v" ]; then
        REMOVE_VOLUMES=true
        print_color "$RED" "⚠ WARNING: This will remove all data volumes!"
        print_color "$YELLOW" "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
        sleep 5
    fi
    
    # Stop services
    print_color "$BLUE" "Stopping Docker containers..."
    
    if [ "$REMOVE_VOLUMES" = true ]; then
        docker-compose down -v
        if [ $? -eq 0 ]; then
            print_color "$GREEN" "✓ Services stopped and volumes removed"
        else
            print_color "$RED" "❌ Failed to stop services"
            exit 1
        fi
    else
        docker-compose down
        if [ $? -eq 0 ]; then
            print_color "$GREEN" "✓ Services stopped successfully"
        else
            print_color "$RED" "❌ Failed to stop services"
            exit 1
        fi
    fi
    
    # Show remaining containers
    print_header "Remaining ATMS Containers"
    running_containers=$(docker ps -a --filter "name=traffic-" --format "table {{.Names}}\t{{.Status}}" | tail -n +2)
    
    if [ -z "$running_containers" ]; then
        print_color "$GREEN" "✓ No ATMS containers running"
    else
        print_color "$YELLOW" "⚠ Some containers are still present:"
        echo "$running_containers"
        echo ""
        print_color "$YELLOW" "To remove them, run:"
        echo "  docker rm -f \$(docker ps -a --filter \"name=traffic-\" -q)"
    fi
    
    # Show cleanup commands
    if [ "$REMOVE_VOLUMES" = false ]; then
        print_header "Cleanup Options"
        echo ""
        print_color "$YELLOW" "To also remove all data volumes (WARNING: deletes all data):"
        echo "  ./stop.sh --clean"
        echo ""
        print_color "$YELLOW" "To remove Docker images:"
        echo "  docker-compose down --rmi all"
        echo ""
    fi
    
    print_header "System Stopped"
    print_color "$GREEN" "ATMS services have been stopped."
    echo ""
    print_color "$BLUE" "To start again, run: ./start.sh"
    echo ""
}

# Run main function
main "$@"

