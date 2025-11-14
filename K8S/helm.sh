#!/bin/bash
set -e

echo "[INFO] Downloading Helm installation script..."
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4

echo "[INFO] Making script executable..."
chmod 700 get_helm.sh


echo "[INFO] Installing the latest Helm version..."
./get_helm.sh

echo "[INFO] Verifying Helm installation..."
helm version

echo "[SUCCESS] Helm latest version installed successfully."
