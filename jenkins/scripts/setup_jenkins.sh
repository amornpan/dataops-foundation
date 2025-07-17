#!/bin/bash
# Jenkins Setup Helper Script
# สคริปต์ช่วยตั้งค่า Jenkins สำหรับ DataOps Foundation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🔧 DataOps Foundation Jenkins Setup Helper"
    echo "=================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        docker --version
    else
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose is installed"
        docker-compose --version
    else
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if DataOps Foundation project exists
    if [[ ! -f "docker/Dockerfile.jenkins" ]]; then
        print_error "DataOps Foundation project not found. Please run this script from the project root."
        exit 1
    fi
    
    print_success "All prerequisites are met"
}

setup_environment() {
    print_step "Setting up environment..."
    
    # Create .env file if not exists
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Jenkins Configuration
JENKINS_ADMIN_PASSWORD=DataOps123!
JENKINS_URL=http://localhost:8081/

# GitHub Configuration
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-github-token

# Database Configuration
DB_USERNAME=sa
DB_PASSWORD=DataOps123!

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Docker Hub Configuration
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-token
EOF
        print_warning "Created .env file with default values. Please update it with your actual credentials."
        print_warning "Edit .env file: nano .env"
        read -p "Press Enter to continue after updating .env file..."
    else
        print_success ".env file already exists"
    fi
}

build_jenkins_image() {
    print_step "Building Jenkins Docker image with Python and DataOps tools..."
    
    docker build -f docker/Dockerfile.jenkins -t dataops-jenkins . || {
        print_error "Failed to build Jenkins image"
        exit 1
    }
    
    print_success "Jenkins image built successfully"
}

create_docker_network() {
    print_step "Creating Docker network..."
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q "dataops-network"; then
        docker network create dataops-network
        print_success "Docker network 'dataops-network' created"
    else
        print_success "Docker network 'dataops-network' already exists"
    fi
}

start_jenkins() {
    print_step "Starting Jenkins container..."
    
    # Stop existing container if running
    if docker ps -a | grep -q "dataops-jenkins"; then
        print_warning "Stopping existing Jenkins container..."
        docker stop dataops-jenkins || true
        docker rm dataops-jenkins || true
    fi
    
    # Start Jenkins container
    docker run -d \
        --name dataops-jenkins \
        --network dataops-network \
        -p 8081:8080 \
        -p 50000:50000 \
        -v jenkins-data:/var/jenkins_home \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "$(pwd)":/workspace \
        --env-file .env \
        -e TZ=Asia/Bangkok \
        -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
        -e CASC_JENKINS_CONFIG="/var/jenkins_home/casc_configs/jenkins.yaml" \
        --restart unless-stopped \
        dataops-jenkins || {
        print_error "Failed to start Jenkins container"
        exit 1
    }
    
    print_success "Jenkins container started"
}

wait_for_jenkins() {
    print_step "Waiting for Jenkins to start..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:8081/login > /dev/null 2>&1; then
            print_success "Jenkins is running and accessible"
            return 0
        fi
        
        echo -n "."
        sleep 10
        ((attempt++))
    done
    
    print_error "Jenkins failed to start within expected time"
    print_warning "Check logs: docker logs dataops-jenkins"
    exit 1
}

get_initial_password() {
    print_step "Getting Jenkins initial admin password..."
    
    # Wait a bit more for Jenkins to fully initialize
    sleep 10
    
    local password
    password=$(docker exec dataops-jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "")
    
    if [[ -n "$password" ]]; then
        echo ""
        echo "=================================================="
        echo "🔑 Jenkins Initial Admin Password:"
        echo "   $password"
        echo "=================================================="
        echo ""
    else
        print_warning "Initial password not found (Jenkins may be using Configuration as Code)"
        print_warning "Default admin credentials:"
        echo "   Username: admin"
        echo "   Password: DataOps123!"
    fi
}

display_access_info() {
    print_step "Displaying access information..."
    
    echo ""
    echo "=================================================="
    echo "🚀 DataOps Foundation Jenkins Setup Complete!"
    echo "=================================================="
    echo ""
    echo "📋 Access Information:"
    echo "   🌐 Jenkins URL: http://localhost:8081"
    echo "   👤 Username: admin"
    echo "   🔐 Password: DataOps123! (or see above)"
    echo ""
    echo "📊 Additional Services:"
    echo "   🎯 Prometheus: http://localhost:9090 (if running full stack)"
    echo "   📈 Grafana: http://localhost:3000 (admin/DataOps123!)"
    echo ""
    echo "🔧 Next Steps:"
    echo "   1. Access Jenkins at http://localhost:8081"
    echo "   2. Log in with admin credentials"
    echo "   3. Update GitHub credentials in Jenkins"
    echo "   4. Test the DataOps Foundation pipeline"
    echo "   5. Configure GitHub webhooks"
    echo ""
    echo "📚 Documentation:"
    echo "   📖 Jenkins Setup: docs/jenkins-setup.md"
    echo "   🚀 Quick Start: docs/quick-start.md"
    echo ""
    echo "🛠️ Useful Commands:"
    echo "   View logs: docker logs -f dataops-jenkins"
    echo "   Restart: docker restart dataops-jenkins"
    echo "   Stop: docker stop dataops-jenkins"
    echo "   Full stack: docker-compose -f docker/docker-compose.yml up -d"
    echo ""
}

show_troubleshooting() {
    print_step "Common troubleshooting steps..."
    
    echo ""
    echo "🔧 Troubleshooting:"
    echo ""
    echo "1. If Jenkins doesn't start:"
    echo "   docker logs dataops-jenkins"
    echo ""
    echo "2. If port 8081 is busy:"
    echo "   sudo lsof -i :8081"
    echo "   # Or change port in docker run command"
    echo ""
    echo "3. If Python not found in Jenkins:"
    echo "   docker exec dataops-jenkins python3 --version"
    echo "   # Should show Python 3.11+"
    echo ""
    echo "4. To restart everything:"
    echo "   docker stop dataops-jenkins && docker rm dataops-jenkins"
    echo "   ./jenkins/setup_jenkins.sh"
    echo ""
}

main() {
    print_header
    
    check_prerequisites
    setup_environment
    create_docker_network
    build_jenkins_image
    start_jenkins
    wait_for_jenkins
    get_initial_password
    display_access_info
    show_troubleshooting
    
    print_success "Jenkins setup completed successfully! 🎉"
}

# Handle script interruption
trap 'print_error "Setup interrupted"; exit 1' INT TERM

# Run main function
main "$@"
