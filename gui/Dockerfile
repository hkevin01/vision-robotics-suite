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
