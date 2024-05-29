FROM docker:latest

# Install necessary packages for Trivy
RUN apk update && apk add wget gnupg

# Download Trivy binary and set permissions
RUN wget -qO /usr/local/bin/trivy https://github.com/aquasecurity/trivy/releases/download/v0.19.2/trivy_0.19.2_Linux-64bit.tar.gz && \
    tar zxvf /usr/local/bin/trivy -C /usr/local/bin/ --strip-components 1 && \
    chmod +x /usr/local/bin/trivy