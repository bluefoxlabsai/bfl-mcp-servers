# Makefile for Google Search MCP Server

# Variables
CHART_NAME = google-search-mcp-server
RELEASE_NAME = google-search-mcp
NAMESPACE = default
HELM_CHART_PATH = ./helm/$(CHART_NAME)

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
	docker build -t $(CHART_NAME):latest .

.PHONY: docker-run
docker-run: ## Run Docker container locally
	docker run -p 8080:8080 \
		-e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
		-e GOOGLE_CSE_ID=${GOOGLE_CSE_ID} \
		$(CHART_NAME):latest

##@ Helm
.PHONY: helm-lint
helm-lint: ## Lint Helm chart
	helm lint $(HELM_CHART_PATH)

.PHONY: helm-template
helm-template: ## Generate Kubernetes manifests from Helm chart
	helm template $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set googleApi.apiKey="test-key" \
		--set googleApi.cseId="test-cse-id"

.PHONY: helm-install
helm-install: ## Install Helm chart
	@if [ -z "$(GOOGLE_API_KEY)" ] || [ -z "$(GOOGLE_CSE_ID)" ]; then \
		echo "Error: GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set"; \
		exit 1; \
	fi
	helm install $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set googleApi.apiKey="$(GOOGLE_API_KEY)" \
		--set googleApi.cseId="$(GOOGLE_CSE_ID)" \
		--namespace $(NAMESPACE)

.PHONY: helm-upgrade
helm-upgrade: ## Upgrade Helm release
	@if [ -z "$(GOOGLE_API_KEY)" ] || [ -z "$(GOOGLE_CSE_ID)" ]; then \
		echo "Error: GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables must be set"; \
		exit 1; \
	fi
	helm upgrade $(RELEASE_NAME) $(HELM_CHART_PATH) \
		--set googleApi.apiKey="$(GOOGLE_API_KEY)" \
		--set googleApi.cseId="$(GOOGLE_CSE_ID)" \
		--namespace $(NAMESPACE)

.PHONY: helm-uninstall
helm-uninstall: ## Uninstall Helm release
	helm uninstall $(RELEASE_NAME) --namespace $(NAMESPACE)

.PHONY: helm-status
helm-status: ## Check Helm release status
	helm status $(RELEASE_NAME) --namespace $(NAMESPACE)

.PHONY: helm-prod-install
helm-prod-install: ## Install with production values
	@if [ ! -f "my-values.yaml" ]; then \
		echo "Error: my-values.yaml not found. Copy and customize values-production.yaml"; \
		exit 1; \
	fi
	helm install $(RELEASE_NAME) $(HELM_CHART_PATH) -f my-values.yaml --namespace $(NAMESPACE)

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

##@ Cleanup
.PHONY: clean
clean: ## Clean up local files
	rm -rf .venv/
	rm -f my-values.yaml
	docker rmi $(CHART_NAME):latest 2>/dev/null || true