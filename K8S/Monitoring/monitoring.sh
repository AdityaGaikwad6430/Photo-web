#!/bin/bash
set -e

echo "[INFO] Adding Helm repos..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "[INFO] Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

echo "[INFO] Installing kube-prometheus-stack..."
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring

echo "[INFO] Waiting for pods to be ready..."
sleep 15

echo "[INFO] Detecting Grafana selector..."
GRAFANA_SELECTOR=$(kubectl get pods -n monitoring -l "app.kubernetes.io/name=grafana" --no-headers | head -n1 | awk '{print $1}')
if [ -z "$GRAFANA_SELECTOR" ]; then
  echo "[ERROR] Could not find Grafana pod. Aborting."
  exit 1
fi

echo "[INFO] Creating Grafana NodePort service..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: grafana-nodeport
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: grafana
  ports:
  - port: 80
    targetPort: 3000
    nodePort: 32001
EOF

echo "[INFO] Creating Prometheus NodePort service..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: prometheus-nodeport
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: prometheus
  ports:
  - port: 9090
    targetPort: 9090
    nodePort: 32090
EOF

echo "[INFO] Creating Alertmanager NodePort service..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: alertmanager-nodeport
  namespace: monitoring
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: alertmanager
  ports:
  - port: 9093
    targetPort: 9093
    nodePort: 32091
EOF

echo "[INFO] Fetching Grafana admin password..."
GRAFANA_PASS=$(kubectl get secret --namespace monitoring monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode)

echo "--------------------------------------------"
echo "   🎉 Monitoring stack installation complete"
echo "--------------------------------------------"
echo "Grafana:"
echo "  URL: http://<node-ip>:32001"
echo "  User: admin"
echo "  Password: $GRAFANA_PASS"
echo ""
echo "Prometheus:"
echo "  URL: http://<node-ip>:32090"
echo ""
echo "Alertmanager:"
echo "  URL: http://<node-ip>:32091"
echo "--------------------------------------------"
