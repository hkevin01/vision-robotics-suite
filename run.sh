#!/bin/bash
# Vision Robotics Suite - Docker Orchestration Script
# Robust Docker-first orchestration with automatic GUI generation

set -Eeuo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration with environment variable support
IMAGE_NAME="${IMAGE_NAME:-vision-robotics-api:local}"
GUI_IMAGE_NAME="${GUI_IMAGE_NAME:-vision-robotics-gui:local}"
SERVICE_NAME="${SERVICE_NAME:-api}"
GUI_SERVICE_NAME="${GUI_SERVICE_NAME:-gui}"
ENV_FILE="${ENV_FILE:-.env}"
PORTS="${PORTS:-8000:8000}"
GUI_PORT="${GUI_PORT:-3000}"
API_URL="${API_URL:-http://localhost:8000}"
GUI_PATH="${GUI_PATH:-./gui}"
DEV_MODE="${DEV_MODE:-false}"
DOCKER_PLATFORM="${DOCKER_PLATFORM:-}"
MOUNTS="${MOUNTS:-}"
BUILD_ARGS="${BUILD_ARGS:-}"

# Script constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.yml"
REPO_ROOT="$SCRIPT_DIR"

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Error handling
trap 'echo -e "${RED}❌ Error occurred on line $LINENO. Check logs above.${NC}" >&2; exit 1' ERR

# Utility functions
log_info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

log_error() {
    echo -e "${RED}❌ $*${NC}" >&2
}

log_step() {
    echo -e "${CYAN}🔄 $*${NC}"
}

# Preflight checks
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker CLI not found. Please install Docker."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Cannot connect to Docker daemon. Is Docker running?"
        exit 1
    fi

    log_success "Docker CLI and daemon are available"
}

check_compose() {
    # Prefer 'docker compose' over 'docker-compose'
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
        log_success "Using 'docker compose' (v2)"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        log_warning "Using legacy 'docker-compose' (v1)"
    else
        log_error "Neither 'docker compose' nor 'docker-compose' found"
        exit 1
    fi
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Linux*)     PLATFORM=Linux;;
        Darwin*)    PLATFORM=Mac;;
        *)          PLATFORM="Unknown";;
    esac
    log_info "Detected platform: $PLATFORM"
}

# GUI existence and creation
check_gui_exists() {
    if [[ -d "$GUI_PATH" && -f "$GUI_PATH/index.html" ]]; then
        return 0
    else
        return 1
    fi
}

create_gui_scaffold() {
    local force_create=${1:-false}

    if check_gui_exists && [[ "$force_create" != "true" ]]; then
        log_warning "GUI already exists at $GUI_PATH. Use --force to overwrite."
        return 0
    fi

    log_step "Creating minimal responsive GUI scaffold at $GUI_PATH"

    mkdir -p "$GUI_PATH"

    # Create index.html
    cat > "$GUI_PATH/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vision Robotics Suite</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>
                <svg class="logo" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                Vision Robotics Suite
            </h1>
            <p class="subtitle">Industrial Automation & Machine Vision Dashboard</p>
        </header>

        <main class="main">
            <section class="status-panel">
                <h2>System Status</h2>
                <div class="status-grid">
                    <div class="status-card" id="api-status">
                        <div class="status-indicator"></div>
                        <div class="status-content">
                            <h3>API Server</h3>
                            <p class="status-text">Checking...</p>
                        </div>
                    </div>
                    <div class="status-card" id="vision-status">
                        <div class="status-indicator"></div>
                        <div class="status-content">
                            <h3>Vision Systems</h3>
                            <p class="status-text">Offline</p>
                        </div>
                    </div>
                    <div class="status-card" id="robot-status">
                        <div class="status-indicator"></div>
                        <div class="status-content">
                            <h3>Robot Control</h3>
                            <p class="status-text">Offline</p>
                        </div>
                    </div>
                </div>
            </section>

            <section class="control-panel">
                <h2>Quick Actions</h2>
                <div class="action-grid">
                    <button class="action-btn primary" onclick="app.runDemo()">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8,5.14V19.14L19,12.14L8,5.14Z" />
                        </svg>
                        Run Demo
                    </button>
                    <button class="action-btn secondary" onclick="app.checkHealth()">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12,2C13.1,2 14,2.9 14,4C14,5.1 13.1,6 12,6C10.9,6 10,5.1 10,4C10,2.9 10.9,2 12,2M21,9V7L19,5.5C18.9,5.4 18.8,5.4 18.7,5.4C18.6,5.4 18.5,5.4 18.4,5.5L17,6.5C16.7,6.7 16.7,7.1 17,7.3L18.5,8.5V10.5L17,11.7C16.7,11.9 16.7,12.3 17,12.5L18.4,13.5C18.5,13.6 18.6,13.6 18.7,13.6C18.8,13.6 18.9,13.6 19,13.5L21,12V10H21V9M6.5,10H4.5C4.2,10 4,10.2 4,10.5V13.5C4,13.8 4.2,14 4.5,14H6.5C6.8,14 7,13.8 7,13.5V10.5C7,10.2 6.8,10 6.5,10Z"/>
                        </svg>
                        Health Check
                    </button>
                    <button class="action-btn secondary" onclick="app.openDocs()">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z"/>
                        </svg>
                        Documentation
                    </button>
                </div>
            </section>

            <section class="demo-panel">
                <h2>Vision System Demos</h2>
                <div class="demo-grid">
                    <div class="demo-card">
                        <h3>Paint Inspection</h3>
                        <p>Automotive paint defect detection</p>
                        <button onclick="app.runVisionDemo('paint')" class="demo-btn">Run Demo</button>
                    </div>
                    <div class="demo-card">
                        <h3>3D Registration</h3>
                        <p>Point cloud alignment and registration</p>
                        <button onclick="app.runVisionDemo('3d')" class="demo-btn">Run Demo</button>
                    </div>
                    <div class="demo-card">
                        <h3>Robot Safety</h3>
                        <p>Collaborative safety zones</p>
                        <button onclick="app.runVisionDemo('safety')" class="demo-btn">Run Demo</button>
                    </div>
                </div>
            </section>

            <section class="logs-panel">
                <h2>System Logs</h2>
                <div class="logs-container">
                    <pre id="logs-output">Waiting for system status...</pre>
                </div>
                <button onclick="app.clearLogs()" class="clear-logs-btn">Clear Logs</button>
            </section>
        </main>

        <footer class="footer">
            <p>&copy; 2025 Vision Robotics Suite - Industrial Automation Platform</p>
        </footer>
    </div>

    <script src="app.js"></script>
</body>
</html>
EOF

    # Create styles.css
    cat > "$GUI_PATH/styles.css" << 'EOF'
/* Vision Robotics Suite - Responsive Styles */
:root {
    --primary-color: #2563eb;
    --primary-dark: #1d4ed8;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    padding: 2rem 1rem;
    text-align: center;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.logo {
    width: 3rem;
    height: 3rem;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    font-weight: 300;
}

/* Main Content */
.main {
    flex: 1;
    padding: 2rem 1rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

.main section {
    background: var(--card-bg);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-color);
}

.main h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}

/* Status Panel */
.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.status-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    background: var(--card-bg);
}

.status-indicator {
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    background-color: var(--secondary-color);
    flex-shrink: 0;
    transition: background-color 0.3s ease;
}

.status-card.online .status-indicator {
    background-color: var(--success-color);
}

.status-card.error .status-indicator {
    background-color: var(--error-color);
}

.status-content h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.status-text {
    font-size: 0.875rem;
    color: var(--text-secondary);
}

/* Action Panel */
.action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    background: var(--card-bg);
    color: var(--text-primary);
    border: 2px solid var(--border-color);
}

.action-btn svg {
    width: 1.25rem;
    height: 1.25rem;
}

.action-btn.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

.action-btn.primary:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.action-btn.secondary:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

/* Demo Panel */
.demo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.demo-card {
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.demo-card:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.demo-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.demo-card p {
    color: var(--text-secondary);
    margin-bottom: 1rem;
    font-size: 0.875rem;
}

.demo-btn {
    padding: 0.5rem 1rem;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.demo-btn:hover {
    background: var(--primary-dark);
}

/* Logs Panel */
.logs-container {
    background: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    line-height: 1.4;
}

#logs-output {
    white-space: pre-wrap;
    word-wrap: break-word;
}

.clear-logs-btn {
    padding: 0.5rem 1rem;
    background: var(--secondary-color);
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.clear-logs-btn:hover {
    background: #475569;
}

/* Footer */
.footer {
    background: var(--text-primary);
    color: white;
    padding: 1rem;
    text-align: center;
    font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
        flex-direction: column;
        gap: 0.5rem;
    }

    .logo {
        width: 2.5rem;
        height: 2.5rem;
    }

    .main {
        padding: 1rem 0.5rem;
    }

    .main section {
        padding: 1rem;
        margin-bottom: 1.5rem;
    }

    .status-grid,
    .action-grid,
    .demo-grid {
        grid-template-columns: 1fr;
    }

    .action-btn {
        padding: 0.875rem 1.25rem;
    }
}

@media (max-width: 480px) {
    .header {
        padding: 1.5rem 0.5rem;
    }

    .header h1 {
        font-size: 1.75rem;
    }

    .subtitle {
        font-size: 1rem;
    }

    .main section {
        margin-bottom: 1rem;
    }
}

/* Animations */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.status-indicator.checking {
    animation: pulse 1.5s infinite;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Focus styles for keyboard navigation */
button:focus,
.action-btn:focus,
.demo-btn:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}
EOF

    # Create app.js
    cat > "$GUI_PATH/app.js" << 'EOF'
// Vision Robotics Suite - Frontend Application
class VisionRoboticsApp {
    constructor() {
        this.config = {
            apiUrl: this.getApiUrl(),
            updateInterval: 5000,
            maxLogLines: 100
        };

        this.logs = [];
        this.statusCheckInterval = null;

        this.init();
    }

    getApiUrl() {
        // Try to load from config.json first, then fall back to window.ENV or default
        if (window.ENV && window.ENV.API_URL) {
            return window.ENV.API_URL;
        }

        // Default API URL (will be replaced by Docker configuration)
        return window.location.protocol + '//' + window.location.hostname + ':8000';
    }

    init() {
        this.log('🚀 Vision Robotics Suite GUI initialized');
        this.log(`📡 API URL: ${this.config.apiUrl}`);

        // Load configuration
        this.loadConfig();

        // Start status monitoring
        this.startStatusMonitoring();

        // Initial status check
        this.checkSystemStatus();
    }

    async loadConfig() {
        try {
            const response = await fetch('./config.json');
            if (response.ok) {
                const config = await response.json();
                this.config = { ...this.config, ...config };
                this.log('⚙️ Configuration loaded from config.json');
            }
        } catch (error) {
            this.log('⚠️ Using default configuration (config.json not found)');
        }
    }

    startStatusMonitoring() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }

        this.statusCheckInterval = setInterval(() => {
            this.checkSystemStatus();
        }, this.config.updateInterval);
    }

    async checkSystemStatus() {
        this.updateStatusIndicator('api-status', 'checking');

        try {
            const response = await fetch(`${this.config.apiUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });

            if (response.ok) {
                const data = await response.json();
                this.updateStatusIndicator('api-status', 'online', 'Connected');
                this.log(`✅ API health check passed: ${JSON.stringify(data)}`);

                // Check other system components
                this.checkVisionSystems();
                this.checkRobotSystems();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.updateStatusIndicator('api-status', 'error', `Error: ${error.message}`);
            this.log(`❌ API health check failed: ${error.message}`);

            // Reset other systems to offline
            this.updateStatusIndicator('vision-status', 'offline', 'Offline');
            this.updateStatusIndicator('robot-status', 'offline', 'Offline');
        }
    }

    async checkVisionSystems() {
        try {
            const response = await fetch(`${this.config.apiUrl}/api/vision/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatusIndicator('vision-status', 'online', 'Systems Online');
                this.log(`🔍 Vision systems status: ${data.systems_count || 0} systems active`);
            } else {
                this.updateStatusIndicator('vision-status', 'offline', 'Not Available');
            }
        } catch (error) {
            this.updateStatusIndicator('vision-status', 'offline', 'Offline');
        }
    }

    async checkRobotSystems() {
        try {
            const response = await fetch(`${this.config.apiUrl}/api/robots/status`);
            if (response.ok) {
                const data = await response.json();
                this.updateStatusIndicator('robot-status', 'online', 'Connected');
                this.log(`🤖 Robot systems status: ${data.robots_count || 0} robots connected`);
            } else {
                this.updateStatusIndicator('robot-status', 'offline', 'Not Available');
            }
        } catch (error) {
            this.updateStatusIndicator('robot-status', 'offline', 'Offline');
        }
    }

    updateStatusIndicator(elementId, status, message = '') {
        const element = document.getElementById(elementId);
        if (!element) return;

        const indicator = element.querySelector('.status-indicator');
        const text = element.querySelector('.status-text');

        // Remove existing status classes
        element.classList.remove('online', 'offline', 'error', 'checking');
        indicator.classList.remove('checking');

        // Add new status
        element.classList.add(status);
        if (status === 'checking') {
            indicator.classList.add('checking');
        }

        if (text && message) {
            text.textContent = message;
        }
    }

    async runDemo() {
        this.log('🎬 Starting complete vision robotics demo...');

        try {
            const response = await fetch(`${this.config.apiUrl}/api/demo/run`, {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json();
                this.log(`✅ Demo completed successfully in ${data.duration}s`);
                this.log(`📊 Results: ${JSON.stringify(data.results, null, 2)}`);
            } else {
                throw new Error(`Demo failed: HTTP ${response.status}`);
            }
        } catch (error) {
            this.log(`❌ Demo failed: ${error.message}`);
        }
    }

    async runVisionDemo(type) {
        this.log(`🔍 Starting ${type} vision demo...`);

        try {
            const response = await fetch(`${this.config.apiUrl}/api/demo/vision/${type}`, {
                method: 'POST'
            });

            if (response.ok) {
                const data = await response.json();
                this.log(`✅ ${type} demo completed: ${JSON.stringify(data, null, 2)}`);
            } else {
                throw new Error(`Demo failed: HTTP ${response.status}`);
            }
        } catch (error) {
            this.log(`❌ ${type} demo failed: ${error.message}`);
        }
    }

    async checkHealth() {
        this.log('🏥 Running comprehensive health check...');
        await this.checkSystemStatus();
    }

    openDocs() {
        const docsUrl = `${this.config.apiUrl}/docs`;
        window.open(docsUrl, '_blank');
        this.log(`📚 Opening API documentation: ${docsUrl}`);
    }

    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${message}`;

        this.logs.push(logEntry);

        // Limit log history
        if (this.logs.length > this.config.maxLogLines) {
            this.logs = this.logs.slice(-this.config.maxLogLines);
        }

        // Update UI
        const logsOutput = document.getElementById('logs-output');
        if (logsOutput) {
            logsOutput.textContent = this.logs.join('\n');
            logsOutput.scrollTop = logsOutput.scrollHeight;
        }
    }

    clearLogs() {
        this.logs = [];
        const logsOutput = document.getElementById('logs-output');
        if (logsOutput) {
            logsOutput.textContent = 'Logs cleared.';
        }
        this.log('🧹 Logs cleared');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VisionRoboticsApp();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.app) {
        if (document.hidden) {
            // Pause monitoring when tab is hidden
            if (window.app.statusCheckInterval) {
                clearInterval(window.app.statusCheckInterval);
            }
        } else {
            // Resume monitoring when tab becomes visible
            window.app.startStatusMonitoring();
            window.app.checkSystemStatus();
        }
    }
});
EOF

    # Create config.json for API URL configuration
    cat > "$GUI_PATH/config.json" << EOF
{
    "API_URL": "$API_URL",
    "updateInterval": 5000,
    "maxLogLines": 100
}
EOF

    # Create GUI Dockerfile
    cat > "$GUI_PATH/Dockerfile" << 'EOF'
# Vision Robotics Suite - GUI Container
FROM nginx:alpine

# Copy GUI files
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY config.json /usr/share/nginx/html/

# Create nginx configuration
RUN cat > /etc/nginx/conf.d/default.conf << 'EOL'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Gzip configuration
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOL

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80
EOF

    log_success "GUI scaffold created successfully at $GUI_PATH"
}

# Compose file generation
create_compose_file() {
    log_step "Creating docker-compose.yml"

    # Parse backend port
    local backend_port_mapping="$PORTS"
    local backend_internal_port="${backend_port_mapping##*:}"

    cat > "$COMPOSE_FILE" << EOF
# Vision Robotics Suite - Docker Compose Configuration
version: '3.8'

services:
  $SERVICE_NAME:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - BUILDKIT_INLINE_CACHE=1
$(if [[ -n "$DOCKER_PLATFORM" ]]; then echo "      - DOCKER_PLATFORM=$DOCKER_PLATFORM"; fi)
$(if [[ -n "$BUILD_ARGS" ]]; then
    IFS=' ' read -ra ARGS <<< "$BUILD_ARGS"
    for arg in "${ARGS[@]}"; do
        echo "        - $arg"
    done
fi)
    image: $IMAGE_NAME
    container_name: ${SERVICE_NAME}-container
    ports:
      - "$backend_port_mapping"
$(if [[ -f "$ENV_FILE" ]]; then echo "    env_file: $ENV_FILE"; fi)
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
$(if [[ -n "$MOUNTS" ]]; then
    echo "    volumes:"
    IFS=',' read -ra MOUNT_ARRAY <<< "$MOUNTS"
    for mount in "${MOUNT_ARRAY[@]}"; do
        mount=$(echo "$mount" | xargs) # trim whitespace
        echo "      - $mount"
    done
fi)
    networks:
      - vision-robotics-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "import requests; requests.get('http://localhost:$backend_internal_port/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

$(if check_gui_exists; then cat << 'COMPOSE_GUI'
  gui:
    build:
      context: ./gui
      dockerfile: Dockerfile
    image: $GUI_IMAGE_NAME
    container_name: ${GUI_SERVICE_NAME}-container
    ports:
      - "$GUI_PORT:80"
    environment:
      - API_URL=http://$SERVICE_NAME:$backend_internal_port
    depends_on:
      - $SERVICE_NAME
    networks:
      - vision-robotics-net
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
COMPOSE_GUI
fi)

networks:
  vision-robotics-net:
    driver: bridge

volumes:
  vision-data:
  logs-data:
EOF

    log_success "docker-compose.yml created"
}

# Backend Dockerfile creation (if missing)
create_backend_dockerfile() {
    if [[ -f "Dockerfile" ]]; then
        log_info "Dockerfile already exists, skipping creation"
        return 0
    fi

    log_step "Creating backend Dockerfile"

    cat > "Dockerfile" << 'EOF'
# Vision Robotics Suite - Production Backend
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt* pyproject.toml* poetry.lock* ./

# Install Python dependencies
RUN if [ -f "pyproject.toml" ]; then \
        pip install poetry && \
        poetry config virtualenvs.create false && \
        poetry install --only=main --no-dev; \
    elif [ -f "requirements.txt" ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        pip install fastapi uvicorn numpy opencv-python; \
    fi

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

    log_success "Dockerfile created"
}

# Command implementations
cmd_help() {
    cat << 'EOF'
Vision Robotics Suite - Docker Orchestration

USAGE:
    ./run.sh <command> [options]

COMMANDS:
    help            Show this help message
    build           Build all container images
    up              Start all services (creates GUI if missing)
    down            Stop and remove all containers
    stop            Stop all services
    restart         Restart all services
    logs [service]  Show logs (default: api service)
    exec [cmd]      Execute command in api container
    shell           Open shell in api container
    ps              Show container status
    clean           Remove containers and images
    prune           Clean up Docker system
    gui:create      Create GUI scaffold (--force to overwrite)
    gui:open        Open GUI in browser
    status          Show detailed system status

ENVIRONMENT VARIABLES:
    IMAGE_NAME              Backend image name (default: vision-robotics-api:local)
    GUI_IMAGE_NAME          GUI image name (default: vision-robotics-gui:local)
    SERVICE_NAME            Backend service name (default: api)
    GUI_SERVICE_NAME        GUI service name (default: gui)
    ENV_FILE               Environment file (default: .env)
    PORTS                  Backend port mapping (default: 8000:8000)
    GUI_PORT               GUI port (default: 3000)
    API_URL                API URL for GUI (default: http://localhost:8000)
    GUI_PATH               GUI directory (default: ./gui)
    DEV_MODE               Enable dev mode (default: false)
    DOCKER_PLATFORM        Docker platform (optional)
    MOUNTS                 Additional volume mounts (comma-separated)
    BUILD_ARGS             Docker build arguments (space-separated)

EXAMPLES:
    ./run.sh up                    # Start all services
    ./run.sh logs api              # Show API logs
    ./run.sh shell                 # Open shell in API container
    ./run.sh gui:create --force    # Force recreate GUI
    ./run.sh exec "pytest tests/"  # Run tests in container

EOF
}

cmd_build() {
    log_step "Building container images"

    check_docker
    check_compose

    create_backend_dockerfile

    if check_gui_exists; then
        create_compose_file
        $COMPOSE_CMD build
    else
        log_info "GUI not found, building backend only"
        docker build -t "$IMAGE_NAME" .
    fi

    log_success "Build completed"
}

cmd_up() {
    log_step "Starting services"

    check_docker
    check_compose

    # Create GUI if missing
    if ! check_gui_exists; then
        log_info "GUI not found, creating scaffold"
        create_gui_scaffold
    fi

    create_backend_dockerfile
    create_compose_file

    $COMPOSE_CMD up -d --build

    log_success "Services started"

    # Show access information
    echo ""
    log_info "🌐 Service Access Points:"
    echo "   • Backend API: http://localhost:${PORTS%:*}"
    if check_gui_exists; then
        echo "   • GUI Dashboard: http://localhost:$GUI_PORT"
    fi
    echo "   • API Documentation: http://localhost:${PORTS%:*}/docs"
}

cmd_down() {
    check_compose
    log_step "Stopping and removing containers"
    $COMPOSE_CMD down
    log_success "Services stopped"
}

cmd_stop() {
    check_compose
    log_step "Stopping services"
    $COMPOSE_CMD stop
    log_success "Services stopped"
}

cmd_restart() {
    check_compose
    log_step "Restarting services"
    $COMPOSE_CMD restart
    log_success "Services restarted"
}

cmd_logs() {
    local service="${1:-$SERVICE_NAME}"
    check_compose
    log_info "Showing logs for service: $service"
    $COMPOSE_CMD logs -f "$service"
}

cmd_exec() {
    local command="${1:-bash}"
    check_compose
    log_info "Executing command in $SERVICE_NAME: $command"
    $COMPOSE_CMD exec "$SERVICE_NAME" $command
}

cmd_shell() {
    check_compose
    log_info "Opening shell in $SERVICE_NAME container"
    $COMPOSE_CMD exec "$SERVICE_NAME" /bin/bash
}

cmd_ps() {
    check_compose
    log_info "Container status:"
    $COMPOSE_CMD ps
}

cmd_clean() {
    check_compose
    log_step "Cleaning up containers and images"
    $COMPOSE_CMD down --rmi all --volumes --remove-orphans
    log_success "Cleanup completed"
}

cmd_prune() {
    check_docker
    log_step "Pruning Docker system"
    docker system prune -f
    log_success "Docker system pruned"
}

cmd_gui_create() {
    local force=false
    if [[ "${1:-}" == "--force" ]]; then
        force=true
    fi

    create_gui_scaffold "$force"
}

cmd_gui_open() {
    local gui_url="http://localhost:$GUI_PORT"

    log_info "Opening GUI at $gui_url"

    case "$PLATFORM" in
        Mac)    open "$gui_url" ;;
        Linux)  xdg-open "$gui_url" ;;
        *)      log_warning "Please open $gui_url in your browser" ;;
    esac
}

cmd_status() {
    check_compose

    echo ""
    log_info "🔍 System Status Report"
    echo "========================"

    echo ""
    echo "📋 Configuration:"
    echo "   • Backend Image: $IMAGE_NAME"
    echo "   • GUI Image: $GUI_IMAGE_NAME"
    echo "   • Backend Port: $PORTS"
    echo "   • GUI Port: $GUI_PORT"
    echo "   • GUI Path: $GUI_PATH"
    echo "   • Environment File: $ENV_FILE"

    echo ""
    echo "🐳 Docker Services:"
    $COMPOSE_CMD ps

    echo ""
    echo "🌐 Health Checks:"
    # Check API health
    if curl -f "http://localhost:${PORTS%:*}/health" &>/dev/null; then
        log_success "API server is healthy"
    else
        log_error "API server is not responding"
    fi

    # Check GUI health
    if check_gui_exists && curl -f "http://localhost:$GUI_PORT/health" &>/dev/null; then
        log_success "GUI is healthy"
    elif check_gui_exists; then
        log_error "GUI is not responding"
    else
        log_warning "GUI not deployed"
    fi
}

# Main command dispatcher
main() {
    # Detect platform
    detect_platform

    # Handle empty command
    if [[ $# -eq 0 ]]; then
        cmd_help
        exit 0
    fi

    local command="$1"
    shift

    case "$command" in
        help|--help|-h)
            cmd_help
            ;;
        build)
            cmd_build
            ;;
        up)
            cmd_up
            ;;
        down)
            cmd_down
            ;;
        stop)
            cmd_stop
            ;;
        restart)
            cmd_restart
            ;;
        logs)
            cmd_logs "$@"
            ;;
        exec)
            cmd_exec "$@"
            ;;
        shell)
            cmd_shell
            ;;
        ps)
            cmd_ps
            ;;
        clean)
            cmd_clean
            ;;
        prune)
            cmd_prune
            ;;
        gui:create)
            cmd_gui_create "$@"
            ;;
        gui:open)
            cmd_gui_open
            ;;
        status)
            cmd_status
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            cmd_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
