#!/bin/bash

CONTAINER_NAME="fantasy-survivors:history-data"

function show_usage() {
    echo "Usage: $0 [start|stop|restart|logs|status|remove]"
    echo "  run   - Start the container"
    echo "  down    - Stop the container"
    echo "  restart - Restart the container"
    echo "  logs    - Show container logs"
    echo "  status  - Show container status"
    echo "  remove  - Remove the container"
}

case "$1" in
    up)
        echo "Starting container..."
        docker build -t ${CONTAINER_NAME} -f Dockerfile.history-data .
        docker run -name nba-history-data ${CONTAINER_NAME}
        ;;
    down)
        echo "Stopping container..."
        docker stop ${CONTAINER_NAME}
        ;;
    restart)
        echo "Restarting container..."
        docker restart ${CONTAINER_NAME}
        ;;
    logs)
        echo "Showing logs (Ctrl+C to exit)..."
        docker logs -f ${CONTAINER_NAME}
        ;;
    status)
        echo "Container status:"
        docker ps -a | grep ${CONTAINER_NAME}
        ;;
    remove)
        echo "Removing container..."
        docker rm -f ${CONTAINER_NAME}
        ;;
    *)
        show_usage
        exit 1
        ;;
esac