# 🦊 BlueFox Labs MCP Servers

<div align="center">

![BlueFox Labs](https://img.shields.io/badge/BlueFox-Labs-blue?style=for-the-badge&logo=firefox&logoColor=white)
![MCP](https://img.shields.io/badge/Model-Context%20Protocol-orange?style=for-the-badge&logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/K8s-Enabled-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)

</div>

---

🚀 **A monolithic repository containing all Model Context Protocol (MCP) servers developed by BlueFox Labs.**

This repository is designed to scale as our organization grows, with each server maintained in its own dedicated directory with standardized tooling and deployment patterns.

## 🏗️ Repository Structure

```
🦊 bfl-mcp-servers/
├── 📁 server-name/
│   ├── 🐍 server.py              # Main server implementation
│   ├── 🐳 Dockerfile             # Container configuration
│   ├── 📋 pyproject.toml         # Python dependencies
│   ├── 📖 README.md              # Server-specific documentation
│   └── ⚓ helm/                  # Kubernetes deployment charts
│       └── 📁 server-name/
│           ├── 📊 Chart.yaml
│           ├── ⚙️ values.yaml
│           └── 📁 templates/
└── 📚 README.md                  # This file
```

## 📦 Available MCP Servers

<div align="center">

| 🚀 Server | 📋 Description | ✨ Key Features |
|-----------|----------------|-----------------|
| **🔍 Google Search MCP** | Web search capabilities through Google API | 🌐 Web search, 🎯 Result filtering, 📄 Content extraction |
| **📈 NASDAQ Data Link MCP** | Financial data access through NASDAQ API | 💰 Equity data, 📊 Market statistics, 📉 Financial indicators |

</div>

### 🔍 Google Search MCP Server
- **📁 Path**: `google-search-mcp/`
- **🎯 Purpose**: Provides comprehensive web search capabilities through Google Search API
- **⚡ Features**: 
  - 🌐 Real-time web search
  - 🎯 Advanced result filtering
  - 📄 Content extraction and summarization

### 📈 NASDAQ Data Link MCP Server
- **📁 Path**: `nasdaq-data-link-mcp/`
- **🎯 Purpose**: Financial data access through NASDAQ Data Link API
- **⚡ Features**: 
  - 💰 Real-time equity data
  - 📊 Market statistics and analytics
  - 📉 Financial indicators and metrics

## 🚀 Getting Started

### 📋 Prerequisites
- 🐍 Python 3.8+
- 🐳 Docker
- ⚓ Kubernetes (for deployment)
- 📊 Helm 3.x

### 💻 Local Development

1. **📥 Clone the repository**
   ```bash
   git clone https://github.com/bluefoxlabsai/bfl-mcp-servers.git
   cd bfl-mcp-servers
   ```

2. **📁 Navigate to a specific server**
   ```bash
   cd <server-name>
   ```

3. **📦 Install dependencies**
   ```bash
   pip install -e .
   ```

4. **🚀 Run the server locally**
   ```bash
   python server.py
   ```

### 🐳 Docker Development

1. **🔧 Build the container**
   ```bash
   cd <server-name>
   docker build -t bfl-<server-name> .
   ```

2. **▶️ Run the container**
   ```bash
   docker run -p 8000:8000 bfl-<server-name>
   ```

### ⚓ Kubernetes Deployment

Each server includes Helm charts for Kubernetes deployment:

```bash
cd <server-name>/helm/<server-name>
helm install <release-name> . -f values.yaml
```

## 🛠️ Development Guidelines

### ➕ Adding a New MCP Server

1. **📁 Create server directory**
   ```bash
   mkdir new-server-name
   cd new-server-name
   ```

2. **📋 Required files structure**
   - 🐍 `server.py` - Main MCP server implementation
   - 📋 `pyproject.toml` - Python package configuration
   - 🐳 `Dockerfile` - Container build instructions
   - 📖 `README.md` - Server-specific documentation
   - ⚓ `helm/` - Kubernetes deployment charts

3. **🏷️ Follow naming conventions**
   - 📁 Directory names: lowercase with hyphens (`my-server-name`)
   - 🐳 Docker images: `bfl-<server-name>`
   - ⚓ Helm releases: `<server-name>-mcp`

### 📏 Code Standards
- ✅ Follow PEP 8 for Python code
- 📝 Include comprehensive docstrings
- 🏷️ Add type hints where applicable
- 🧪 Include unit tests in `tests/` directory
- 📚 Update this README when adding new servers

### 🧪 Testing
```bash
# Run tests for specific server
cd <server-name>
python -m pytest tests/

# Run tests for all servers
python -m pytest */tests/
```

## � Server Status

<div align="center">

| 🚀 Server | 📊 Status | 🏷️ Version | 📅 Last Updated |
|-----------|-----------|-------------|-----------------|
| 🔍 Google Search MCP | ![Active](https://img.shields.io/badge/Status-Active-brightgreen) | ![v1.0.0](https://img.shields.io/badge/Version-v1.0.0-blue) | 2025-09-22 |
| 📈 NASDAQ Data Link MCP | ![Active](https://img.shields.io/badge/Status-Active-brightgreen) | ![v1.0.0](https://img.shields.io/badge/Version-v1.0.0-blue) | 2025-09-22 |

</div>

## ⚙️ Configuration

Each server maintains its own configuration through:
- 🌍 Environment variables
- ⚓ Kubernetes ConfigMaps
- 📊 Helm values files

📖 Refer to individual server READMEs for specific configuration options.

## 🚀 Deployment

### 🏭 Production Deployment
- ⚓ All servers are deployed to Kubernetes clusters
- 📊 Use provided Helm charts for consistent deployments
- 🌍 Environment-specific values files available in `helm/` directories

### 🔄 CI/CD Pipeline
- 🧪 Automated testing on pull requests
- 🐳 Docker image builds on main branch merges
- 📊 Automated Helm chart updates

## 📚 Documentation

- 📖 Each server maintains its own README with specific details
- 🔌 API documentation available within server directories
- 📊 Helm chart documentation in respective `helm/` directories

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/new-server`)
3. ✨ Make your changes following the development guidelines
4. 🧪 Add tests for new functionality
5. 📚 Update documentation
6. 📤 Submit a pull request

## 📞 Support

For questions, issues, or contributions:
- 🐛 Create an issue in this repository
- 👥 Contact the BlueFox Labs development team
- 📖 Check individual server READMEs for specific guidance

## 📄 License

This project is proprietary to BlueFox Labs. All rights reserved.

---

<div align="center">

**🦊 BlueFox Labs** - Building the future of AI-powered solutions

[![Website](https://img.shields.io/badge/Website-bluefoxlabs.ai-blue?style=for-the-badge&logo=firefox&logoColor=white)](https://bluefoxlabs.ai)
[![Email](https://img.shields.io/badge/Email-Contact%20Us-red?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contact@bluefoxlabs.ai)

</div>