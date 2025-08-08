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
