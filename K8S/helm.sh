#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the Helm version to install (optional, defaults to latest if not set)
HELM_VERSION="v3.14.4" 

# Download the Helm installation script
echo "Downloading Helm installation script..."
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

# Make the script executable
echo "Making the script executable..."
chmod +x get_helm.sh

# Execute the installation script
# If a specific version is desired, pass it as an argument
if [ -n "$HELM_VERSION" ]; then
    echo "Installing Helm $HELM_VERSION..."
    ./get_helm.sh --version "$HELM_VERSION"
else
    echo "Installing the latest Helm version..."
    ./get_helm.sh
fi

# Verify Helm installation
echo "Verifying Helm installation..."
helm version

echo "Helm installation complete."