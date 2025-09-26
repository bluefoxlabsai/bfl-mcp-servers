#!/bin/bash

# Slack MCP Server Helm Chart Uninstallation Script
# This script helps uninstall the Slack MCP Server using Helm

set -e

# Configuration
NAMESPACE="${NAMESPACE:-mcp-servers}"
RELEASE_NAME="${RELEASE_NAME:-slack-server-mcp}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed. Please install Helm first."
        exit 1
    fi

    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Check if release exists
check_release_exists() {
    if ! helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
        log_error "Helm release '$RELEASE_NAME' not found in namespace '$NAMESPACE'"
        log_info "Available releases:"
        helm list -n "$NAMESPACE" || true
        exit 1
    fi
}

# Confirm uninstallation
confirm_uninstall() {
    echo "You are about to uninstall the Slack MCP Server:"
    echo "  Release: $RELEASE_NAME"
    echo "  Namespace: $NAMESPACE"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Uninstallation cancelled"
        exit 0
    fi
}

# Uninstall Helm release
uninstall_release() {
    log_info "Uninstalling Slack MCP Server..."

    helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"

    log_success "Helm release uninstalled"
}

# Clean up resources
cleanup_resources() {
    log_info "Cleaning up remaining resources..."

    # Delete PVCs if they exist
    local pvcs=$(kubectl get pvc -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" -o name 2>/dev/null || true)
    if [ -n "$pvcs" ]; then
        log_info "Deleting PVCs..."
        kubectl delete $pvcs -n "$NAMESPACE" --ignore-not-found=true
    fi

    # Delete secrets created by the chart (but not external secrets)
    local secrets=$(kubectl get secret -n "$NAMESPACE" -l "app.kubernetes.io/instance=$RELEASE_NAME" -o name 2>/dev/null || true)
    if [ -n "$secrets" ]; then
        log_warn "Found secrets created by the chart. These may contain sensitive data."
        read -p "Delete these secrets? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete $secrets -n "$NAMESPACE" --ignore-not-found=true
            log_info "Secrets deleted"
        fi
    fi

    log_success "Cleanup completed"
}

# Remove namespace if empty and not default
cleanup_namespace() {
    if [ "$NAMESPACE" != "default" ] && [ "$NAMESPACE" != "kube-system" ] && [ "$NAMESPACE" != "kube-public" ]; then
        local resource_count=$(kubectl get all -n "$NAMESPACE" 2>/dev/null | wc -l)
        if [ "$resource_count" -le 1 ]; then  # Only header line
            log_info "Namespace $NAMESPACE is empty. Removing it."
            kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
            log_success "Namespace removed"
        else
            log_info "Namespace $NAMESPACE still contains resources. Keeping it."
        fi
    fi
}

# Show post-uninstall information
show_post_uninstall_info() {
    log_info "Post-uninstallation information:"
    echo ""
    echo "1. Verify resources are cleaned up:"
    echo "   kubectl get all -n $NAMESPACE"
    echo ""
    echo "2. Check for any remaining PVCs:"
    echo "   kubectl get pvc -n $NAMESPACE"
    echo ""
    echo "3. If you want to completely remove the namespace:"
    echo "   kubectl delete namespace $NAMESPACE"
    echo ""
    echo "4. To reinstall, run the install script:"
    echo "   ./helm/install.sh"
}

# Main uninstallation function
main() {
    echo "Slack MCP Server Uninstallation"
    echo "==============================="
    echo ""

    check_prerequisites
    check_release_exists
    confirm_uninstall
    uninstall_release
    cleanup_resources
    cleanup_namespace
    show_post_uninstall_info

    log_success "Uninstallation completed successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Uninstall the Slack MCP Server using Helm"
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE    Kubernetes namespace (default: mcp-servers)"
    echo "  -r, --release-name NAME      Helm release name (default: slack-mcp)"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 -n my-namespace -r my-release"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release-name)
            RELEASE_NAME="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function
main