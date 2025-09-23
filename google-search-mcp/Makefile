# Makefile for Google Search MCP Server

# Variables
CHART_NAME = google-search-mcp
RELEASE_NAME = google-search-mcp
NAMESPACE = mcp-servers
HELM_CHART_PATH = ./helm
DOCKER_IMAGE = bfljerum/google-search-mcp

# Default target
.DEFAULT_GOAL := help

## Display this help message
help:
	@echo "Google Search MCP Server - Available Commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\033[36m%-30s\033[0m %s\n", "Target", "Description"} /^[a-zA-Z_-]+:.*?##/ { printf "\033[36m%-30s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
.PHONY: install-deps
install-deps: ## Install Python dependencies with uv
	uv sync

.PHONY: run-local
run-local: ## Run the server locally
	uv run google_search_mcp_server.py

.PHONY: test
test: ## Run tests
	uv run python -c "import asyncio; from google_search_mcp_server import search_google; print(asyncio.run(search_google('test', 1)))"

##@ Docker
.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -f Dockerfile.enhanced -t $(DOCKER_IMAGE):latest .

.PHONY: docker-push
docker-push: ## Push Docker image to registry
	docker push $(DOCKER_IMAGE):latest

.PHONY: docker-build-push
docker-build-push: docker-build docker-push ## Build and push Docker image

.PHONY: docker-run
docker-run: ## Run Docker container locally
	docker run -p 8000:8000 \
		-e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
		-e GOOGLE_CSE_ID=${GOOGLE_CSE_ID} \
		$(DOCKER_IMAGE):latest

##@ Helm
.PHONY: helm-lint
helm-lint: ## Lint Helm chart
	helm lint $(HELM_CHART_PATH)

.PHONY: helm-template
helm-template: ## Generate Kubernetes manifests from Helm chart
	helm template $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set secret.googleApiKey="test-key" \
		--set secret.googleCseId="test-cse-id"

.PHONY: helm-install-script
helm-install-script: ## Run interactive Helm installation script
	cd $(HELM_CHART_PATH) && ./install.sh

.PHONY: helm-install
helm-install: ## Install Helm chart (API keys optional)
	helm install $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set secret.googleApiKey="$(if $(GOOGLE_API_KEY),$(GOOGLE_API_KEY),YOUR_GOOGLE_API_KEY_HERE)" \
		--set secret.googleCseId="$(if $(GOOGLE_CSE_ID),$(GOOGLE_CSE_ID),YOUR_GOOGLE_CSE_ID_HERE)" \
		--namespace $(NAMESPACE) --create-namespace

.PHONY: helm-upgrade
helm-upgrade: ## Upgrade Helm release (API keys optional)
	helm upgrade $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set secret.googleApiKey="$(if $(GOOGLE_API_KEY),$(GOOGLE_API_KEY),YOUR_GOOGLE_API_KEY_HERE)" \
		--set secret.googleCseId="$(if $(GOOGLE_CSE_ID),$(GOOGLE_CSE_ID),YOUR_GOOGLE_CSE_ID_HERE)" \
		--namespace $(NAMESPACE)

.PHONY: helm-uninstall
helm-uninstall: ## Uninstall Helm release
	helm uninstall $(RELEASE_NAME) --namespace $(NAMESPACE)

.PHONY: helm-uninstall-script
helm-uninstall-script: ## Run interactive Helm uninstall script
	cd $(HELM_CHART_PATH) && ./uninstall.sh

.PHONY: helm-status
helm-status: ## Check Helm release status
	helm status $(RELEASE_NAME) --namespace $(NAMESPACE)

.PHONY: helm-dry-run
helm-dry-run: ## Dry run Helm installation
	@if [ -z "$(GOOGLE_API_KEY)" ] || [ -z "$(GOOGLE_CSE_ID)" ]; then \
		echo "Error: GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set"; \
		exit 1; \
	fi
	helm install $(RELEASE_NAME) $(HELM_CHART_PATH) --dry-run \
		--set secret.googleApiKey="$(GOOGLE_API_KEY)" \
		--set secret.googleCseId="$(GOOGLE_CSE_ID)" \
		--namespace $(NAMESPACE)

.PHONY: helm-prod-install
helm-prod-install: ## Install with production values
	@if [ ! -f "$(HELM_CHART_PATH)/examples/values-prod.yaml" ]; then \
		echo "Error: $(HELM_CHART_PATH)/examples/values-prod.yaml not found"; \
		exit 1; \
	fi
	@if [ -z "$(GOOGLE_API_KEY)" ] || [ -z "$(GOOGLE_CSE_ID)" ]; then \
		echo "Error: GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set"; \
		exit 1; \
	fi
	helm install $(RELEASE_NAME) $(HELM_CHART_PATH) \
		-f $(HELM_CHART_PATH)/examples/values-prod.yaml \
		--set secret.googleApiKey="$(GOOGLE_API_KEY)" \
		--set secret.googleCseId="$(GOOGLE_CSE_ID)" \
		--namespace $(NAMESPACE) --create-namespace

##@ Kubernetes
.PHONY: k8s-logs
k8s-logs: ## View application logs
	kubectl logs -l "app.kubernetes.io/name=$(CHART_NAME)" --namespace $(NAMESPACE) -f

.PHONY: k8s-status
k8s-status: ## Check Kubernetes resources status
	kubectl get all -l "app.kubernetes.io/name=$(CHART_NAME)" --namespace $(NAMESPACE)

.PHONY: k8s-describe
k8s-describe: ## Describe Kubernetes resources
	kubectl describe deployment $(RELEASE_NAME) --namespace $(NAMESPACE)

.PHONY: k8s-port-forward
k8s-port-forward: ## Port forward to the service (for HTTP transports)
	kubectl port-forward service/$(RELEASE_NAME) 8080:8000 --namespace $(NAMESPACE)

##@ Cleanup
.PHONY: clean
clean: ## Clean up local files
	rm -rf .venv/
	rm -f $(HELM_CHART_PATH)/examples/my-values.yaml
	docker rmi $(DOCKER_IMAGE):latest 2>/dev/null || true