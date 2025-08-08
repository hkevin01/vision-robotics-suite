# Frontend Development Container
# Optimized for modern frontend development workflows
FROM node:20-alpine

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl \
    wget \
    bash \
    zsh \
    vim \
    nano \
    htop \
    tree \
    python3 \
    make \
    g++ \
    # Browser dependencies for testing
    chromium \
    firefox \
    # Image optimization tools
    imagemagick \
    # Development utilities
    jq \
    zip \
    unzip

# Set Chrome path for Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV CHROMIUM_PATH=/usr/bin/chromium-browser

# Install global development tools
RUN npm install -g \
    # Package managers
    yarn \
    pnpm \
    # Build tools
    vite \
    webpack \
    webpack-cli \
    parcel \
    rollup \
    esbuild \
    # Framework CLIs
    @vue/cli \
    @angular/cli \
    create-react-app \
    create-next-app \
    @sveltejs/kit \
    # Development tools
    typescript \
    ts-node \
    nodemon \
    concurrently \
    cross-env \
    # Code quality
    eslint \
    prettier \
    stylelint \
    # Testing tools
    jest \
    vitest \
    cypress \
    playwright \
    # Documentation
    storybook \
    # Utilities
    serve \
    http-server \
    live-server \
    json-server

# Install CSS processors
RUN npm install -g \
    sass \
    less \
    postcss \
    postcss-cli \
    autoprefixer \
    tailwindcss

# Install additional development utilities
RUN npm install -g \
    lighthouse \
    bundlesize \
    size-limit \
    webpack-bundle-analyzer \
    npm-check-updates \
    depcheck

# Create development user
RUN addgroup -g 1000 developer && \
    adduser -D -s /bin/bash -u 1000 -G developer developer

# Switch to development user
USER developer
WORKDIR /home/developer

# Set up shell configuration
RUN echo 'export PATH=$PATH:/home/developer/.local/bin' >> ~/.bashrc && \
    echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias l="ls -CF"' >> ~/.bashrc

# Create workspace and cache directories
RUN mkdir -p /home/developer/workspace \
    /home/developer/.npm-global \
    /home/developer/.yarn \
    /home/developer/.pnpm

# Configure npm to use global directory in home
ENV NPM_CONFIG_PREFIX=/home/developer/.npm-global
ENV PATH=$PATH:/home/developer/.npm-global/bin

# Set working directory
WORKDIR /home/developer/workspace

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node --version && npm --version && yarn --version || exit 1

# Default command
CMD ["/bin/bash"]

# Expose common frontend development ports
EXPOSE 3000 3001 4200 5173 8080 9000
