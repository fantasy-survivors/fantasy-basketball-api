#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
show_usage() {
    echo -e "Usage: ./run-docker.sh [command]"
    echo -e "\nCommands:"
    echo "  up        - Start all services"
    echo "  down      - Stop and remove all containers"
    echo "  restart   - Restart all services"
    echo "  logs      - Show logs from all services"
    echo "  ps        - Show status of services"
    echo "  clean     - Stop containers and remove volumes"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}Error: Docker is not running${NC}"
        exit 1
    fi
}

# Main script logic
case "$1" in
    "up")
        check_docker
        echo -e "${GREEN}Starting services...${NC}"
        docker compose -f docker-compose-local.yaml up --build -d
        ;;
    "down")
        check_docker
        remove -rf /postgres_data
        echo -e "${GREEN}Stopping services...${NC}"
        docker compose -f docker-compose-local.yaml down
        ;;
    "restart")
        check_docker
        echo -e "${GREEN}Restarting services...${NC}"
        remove -rf /postgres_data
        docker compose -f docker-compose-local.yaml down
        docker compose -f docker-compose-local.yaml up --build -d
        ;;
    "logs")
        check_docker
        echo -e "${GREEN}Showing logs...${NC}"
        docker compose -f docker-compose-local.yaml logs -f
        ;;
    "ps")
        check_docker
        echo -e "${GREEN}Showing service status...${NC}"
        docker compose -f docker-compose-local.yaml ps
        ;;
    "clean")
        check_docker
        echo -e "${GREEN}Cleaning up containers and volumes...${NC}"
        docker compose -f docker-compose-local.yaml down -v
        ;;
    *)
        show_usage
        ;;
esac 