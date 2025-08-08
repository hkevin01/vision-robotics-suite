# Multi-purpose Backend Development Container
# Supports Python, Node.js, and other backend technologies
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set locale and timezone
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Core development tools
    build-essential \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    jq \
    unzip \
    zip \
    # Network tools
    netcat \
    telnet \
    nmap \
    # Development libraries
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    # System libraries for computer vision
    libopencv-dev \
    python3-opencv \
    # Database clients
    postgresql-client \
    mysql-client \
    redis-tools \
    # Other utilities
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Python (multiple versions for compatibility)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for python commands
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Install Yarn and PNPM
RUN npm install -g yarn pnpm

# Install Go
ENV GO_VERSION=1.21.5
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz \
    && rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python package managers and tools
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip install poetry pipenv virtualenv

# Install Python development tools
RUN pip install \
    black \
    isort \
    flake8 \
    pylint \
    mypy \
    bandit \
    pytest \
    pytest-cov \
    pytest-xdist \
    pre-commit \
    jupyter \
    ipython \
    # Data science and ML libraries
    numpy \
    pandas \
    matplotlib \
    scikit-learn \
    # Web frameworks
    fastapi \
    django \
    flask \
    # Database libraries
    sqlalchemy \
    psycopg2-binary \
    pymongo \
    redis \
    # API and HTTP libraries
    requests \
    httpx \
    aiohttp

# Install Node.js development tools
RUN npm install -g \
    typescript \
    ts-node \
    eslint \
    prettier \
    jest \
    nodemon \
    pm2 \
    @nestjs/cli \
    create-react-app \
    @vue/cli \
    @angular/cli

# Install Docker CLI (for Docker-in-Docker scenarios)
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install docker-compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Create development user
RUN useradd -m -s /bin/bash -u 1000 developer \
    && usermod -aG sudo developer \
    && echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up development environment
USER developer
WORKDIR /home/developer

# Install user-specific tools
RUN curl -sSfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /home/developer/.local/bin

# Set up shell configuration
RUN echo 'export PATH=$PATH:/home/developer/.local/bin' >> ~/.bashrc \
    && echo 'export GOPATH=/home/developer/go' >> ~/.bashrc \
    && echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc

# Create workspace directory
RUN mkdir -p /home/developer/workspace

# Set working directory
WORKDIR /home/developer/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 --version && node --version && go version || exit 1

# Default command
CMD ["/bin/bash"]

# Expose common development ports
EXPOSE 3000 5000 8000 8080 9000
