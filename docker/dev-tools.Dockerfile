# Development Tools and Utilities Container
# Includes code quality, security, and testing tools
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm \
    openjdk-11-jdk \
    ruby \
    ruby-dev \
    golang-go \
    docker.io \
    docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN pip3 install \
    # Code formatters
    black \
    isort \
    autopep8 \
    # Linters
    flake8 \
    pylint \
    mypy \
    # Security scanners
    bandit \
    safety \
    semgrep \
    # Documentation
    sphinx \
    mkdocs \
    # Testing
    pytest \
    pytest-cov \
    pytest-xdist \
    coverage \
    # Pre-commit hooks
    pre-commit

# Install Node.js tools
RUN npm install -g \
    # Code quality
    eslint \
    prettier \
    jshint \
    # Security
    npm-audit \
    audit-ci \
    # Documentation
    jsdoc \
    typedoc \
    # Testing
    jest \
    mocha \
    nyc \
    # Build tools
    webpack \
    parcel \
    # Utilities
    npm-check-updates \
    depcheck

# Install Go tools
ENV PATH=$PATH:/usr/local/go/bin:/root/go/bin
RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install github.com/securecodewarrior/sast-scan@latest && \
    go install golang.org/x/tools/cmd/goimports@latest && \
    go install github.com/fzipp/gocyclo/cmd/gocyclo@latest

# Install Ruby tools
RUN gem install \
    rubocop \
    brakeman \
    bundler-audit

# Install additional security tools
RUN curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin && \
    curl -L https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64 -o /usr/local/bin/hadolint && \
    chmod +x /usr/local/bin/hadolint

# Install Snyk CLI
RUN npm install -g snyk

# Install SonarQube Scanner
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.8.0.2856-linux.zip && \
    unzip sonar-scanner-cli-4.8.0.2856-linux.zip && \
    mv sonar-scanner-4.8.0.2856-linux /opt/sonar-scanner && \
    ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner && \
    rm sonar-scanner-cli-4.8.0.2856-linux.zip

# Install API documentation tools
RUN npm install -g \
    @apidevtools/swagger-cli \
    redoc-cli \
    @stoplight/prism-cli

# Install performance testing tools
RUN npm install -g \
    lighthouse \
    artillery \
    loadtest

# Install container security tools
RUN curl -L https://github.com/aquasecurity/tfsec/releases/latest/download/tfsec-linux-amd64 -o /usr/local/bin/tfsec && \
    chmod +x /usr/local/bin/tfsec

# Create working directory
WORKDIR /workspace

# Create configuration files directory
RUN mkdir -p /workspace/configs

# Copy tool configuration templates
COPY configs/ /workspace/configs/

# Set up Git hooks directory
RUN mkdir -p /workspace/.git/hooks

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 --version && node --version && go version || exit 1

# Default command
CMD ["/bin/bash", "-c", "echo 'Development tools container ready!' && /bin/bash"]
