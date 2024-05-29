FROM docker:latest

# Install necessary tools and Trivy
RUN apk add --no-cache wget tar ca-certificates \
    && wget -qO- https://github.com/aquasecurity/trivy/releases/latest/download/trivy_$(uname -s)_$(uname -m).tar.gz | tar zxvf - -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/trivy

# Verify Trivy installation
RUN trivy --version
