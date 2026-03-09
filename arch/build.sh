#!/bin/bash
# NeuralOS Build Script
# Usage: ./build.sh [build|run|nsh|test|clean|status|logs|compose]

set -e

IMAGE="neurlos/neurlos:0.1.0"
CONTAINER="nos-primary"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${CYAN}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}>>> $1${NC}"
}

print_error() {
    echo -e "${RED}>>> ERROR: $1${NC}"
}

build() {
    print_info "Building NeuralOS Docker image..."
    docker build -t "$IMAGE" --target nos-full --progress=plain "$SCRIPT_DIR"
    print_success "Build complete: $IMAGE"
}

run() {
    print_info "Starting NeuralOS container..."
    docker run --rm -it \
        --env NODE_ID=primary \
        --env AUTO_LOGIN=true \
        --env DEFAULT_USER=user \
        --env TERM=xterm-256color \
        --env PYTHONPATH=/usr/lib/nos \
        -v nos-home:/home/user \
        -v nos-data:/var/lib/nos \
        -v nos-logs:/var/log/nos \
        -v nos-cache:/var/cache/nos \
        "$IMAGE"
}

nsh() {
    print_info "Starting NeuralOS shell session..."
    docker run --rm -it \
        --env PYTHONPATH=/usr/lib/nos \
        "$IMAGE" /usr/bin/nos-shell
}

shell() {
    print_info "Getting bash shell in running container..."
    docker exec -it "$CONTAINER" /bin/bash
}

test_all() {
    print_info "Running NeuralOS test suite..."
    docker run --rm \
        --env PYTHONPATH=/usr/lib/nos \
        "$IMAGE" python3 /usr/lib/nos/test_all.py
}

status() {
    print_info "NeuralOS Container Status"
    echo ""
    
    if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER"; then
        docker ps -a --filter "name=$CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "Container not found"
    fi
    
    echo ""
    print_info "Image Status"
    docker images "$IMAGE" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

logs() {
    print_info "NeuralOS Init Logs"
    if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER"; then
        docker exec "$CONTAINER" cat /var/log/nos/init.log 2>/dev/null || echo "No logs found"
    else
        echo "Container not running"
    fi
}

clean() {
    print_info "Cleaning up NeuralOS..."
    
    # Stop and remove container
    if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER"; then
        docker rm -f "$CONTAINER" 2>/dev/null || true
    fi
    
    # Remove image
    docker rmi "$IMAGE" 2>/dev/null || true
    
    # Remove volumes
    docker volume rm nos-home nos-data nos-logs nos-cache 2>/dev/null || true
    
    print_success "Cleanup complete"
}

compose_up() {
    print_info "Starting NeuralOS with Docker Compose..."
    cd "$SCRIPT_DIR"
    docker compose up --build -d
    print_success "NeuralOS started"
}

compose_down() {
    print_info "Stopping NeuralOS..."
    cd "$SCRIPT_DIR"
    docker compose down
    print_success "NeuralOS stopped"
}

compose_logs() {
    cd "$SCRIPT_DIR"
    docker compose logs -f
}

show_help() {
    echo "NeuralOS Build System v0.1.0"
    echo ""
    echo "Usage: ./build.sh <command>"
    echo ""
    echo "Commands:"
    echo "  build       Build Docker image"
    echo "  run         Run container interactively"
    echo "  nsh         Start nos-shell session"
    echo "  shell       Get bash shell in running container"
    echo "  test        Run test suite"
    echo "  status      Show container/image status"
    echo "  logs        Show init logs"
    echo "  clean       Remove container, image, and volumes"
    echo "  up          Start with Docker Compose"
    echo "  down        Stop Docker Compose"
    echo "  compose-logs  Show Compose logs"
    echo ""
    echo "Examples:"
    echo "  ./build.sh build    # Build the image"
    echo "  ./build.sh run      # Run interactively"
    echo "  ./build.sh test     # Run tests"
    echo "  ./build.sh up       # Start full stack"
}

# Main
case "${1:-help}" in
    build)
        build
        ;;
    run)
        run
        ;;
    nsh)
        nsh
        ;;
    shell|bash)
        shell
        ;;
    test)
        test_all
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    up|compose)
        compose_up
        ;;
    down)
        compose_down
        ;;
    compose-logs)
        compose_logs
        ;;
    help|-h|--help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
