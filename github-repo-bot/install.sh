#!/bin/bash

# GitHub Repository Enhancement Bot - Installation Script
# Professional setup for repository automation

set -e

echo "🚀 GitHub Repository Enhancement Bot - Installation"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
        MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required (found $PYTHON_VERSION)"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please edit .env and add your GITHUB_TOKEN"
        else
            cat > .env << EOL
# GitHub Repository Enhancement Bot Configuration
GITHUB_TOKEN=your_github_token_here
DEFAULT_PRIVATE=true
DEFAULT_COMMITS=50
DEFAULT_DAYS_BACK=90
EOL
            print_success "Created default .env file"
            print_warning "Please edit .env and add your GITHUB_TOKEN"
        fi
    else
        print_info ".env file already exists"
    fi
}

# Make scripts executable
make_executable() {
    print_info "Making scripts executable..."
    chmod +x bot.py
    chmod +x run_bot.py
    print_success "Scripts are now executable"
}

# Create desktop shortcut (optional)
create_shortcut() {
    if command -v desktop-file-install &> /dev/null; then
        read -p "Create desktop shortcut? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            CURRENT_DIR=$(pwd)
            cat > github-repo-bot.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=GitHub Repo Bot
Comment=Professional GitHub repository enhancement tool
Exec=python3 $CURRENT_DIR/run_bot.py
Icon=utilities-terminal
Terminal=true
Categories=Development;
EOL
            desktop-file-install --dir=$HOME/.local/share/applications github-repo-bot.desktop
            rm github-repo-bot.desktop
            print_success "Desktop shortcut created"
        fi
    fi
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    if python3 bot.py --help &> /dev/null; then
        print_success "Bot executable and working"
    else
        print_error "Bot test failed"
        exit 1
    fi
}

# Main installation process
main() {
    echo
    print_info "Starting installation process..."
    echo
    
    # Check prerequisites
    if ! check_python; then
        print_error "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup environment
    setup_environment
    
    # Make executable
    make_executable
    
    # Test installation
    test_installation
    
    # Optional shortcut
    create_shortcut
    
    echo
    print_success "Installation completed successfully!"
    echo
    print_info "Next steps:"
    echo "  1. Edit .env and add your GITHUB_TOKEN"
    echo "  2. Run: python3 run_bot.py"
    echo "  3. Or use: python3 bot.py --repo-name my-project"
    echo
    print_info "Get your GitHub token at: https://github.com/settings/tokens"
    print_info "Required scopes: repo, delete_repo, user"
    echo
}

# Check if running as source (not via curl)
if [ -f "bot.py" ]; then
    main
else
    print_error "Please run this script from the bot directory"
    exit 1
fi