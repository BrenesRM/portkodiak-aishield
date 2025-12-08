# PortKodiakAIShield

**Windows Application Firewall with ML-based Anomaly Detection**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Privacy-first application firewall for Windows with machine learning-powered anomaly detection. Built with inspiration from [Portmaster](https://github.com/safing/portmaster).

## 🎯 Features

- **Network Connection Interception**: Deep integration with Windows Filtering Platform (WFP)
- **Per-Application Firewall Rules**: Granular control over network access per application
- **ML-Powered Anomaly Detection**: Learn normal behavior and detect suspicious network activity
- **Privacy-First Design**: All analysis runs locally on your machine
- **Real-Time Monitoring**: Live dashboard of network connections and anomalies
- **User Feedback Loop**: Label false positives to improve detection accuracy
- **Configurable Actions**: Notify, block, quarantine, or run custom scripts on anomalies

## 🚀 Quick Start

### Prerequisites

- Windows 10/11 or Windows Server 2016+
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/BrenesRM/portkodiak-aishield.git
cd portkodiak-aishield
```

2. **Install dependencies with uv**
```bash
# Install uv if you haven't already
# Windows: powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

uv sync
```

3. **Run the development environment**
```bash
uv run dev
```

## 📖 Documentation

- [Developer Guide](docs/developer_guide.md) - Setup and contribution guidelines
- [Architecture](docs/architecture.md) - System design and components
- [ML Pipeline](docs/ml_pipeline.md) - Training and deployment workflow
- [User Manual](docs/user_manual.md) - End-user documentation

## 🏗️ Project Structure

```
portkodiak-aishield/
├── app/                    # Main application code
│   ├── service/           # Windows service (core firewall)
│   ├── ui/                # Desktop GUI
│   └── common/            # Shared utilities
├── agent/                 # Kernel/WFP integration
├── ml/                    # Machine learning pipeline
│   ├── notebooks/         # Colab training notebooks
│   ├── models/            # Model implementations
│   └── export/            # ONNX export utilities
├── tests/                 # Test suite
├── packaging/             # Installers and distribution
├── docs/                  # Documentation
└── scripts/               # Development scripts
```

## 🧪 Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linters
uv run ruff check .
uv run black .
uv run mypy app/
```

### Running Components

```bash
# Start the service (requires admin)
uv run portkodiak-service

# Launch the UI
uv run portkodiak-ui

# Run development mode (both)
uv run dev
```

## 🤖 ML Pipeline

Train models using Google Colab:

1. Capture baseline network data (7+ days recommended)
2. Export baseline to CSV/Parquet
3. Open `ml/notebooks/colab_baseline.ipynb` in Google Colab
4. Train Isolation Forest + Autoencoder models
5. Export to ONNX format
6. Load model in PortKodiakAIShield

See [ML Pipeline Documentation](docs/ml_pipeline.md) for details.

## 📦 Building

```bash
# Build installer
uv run scripts/build.py

# Sign code (requires certificate)
uv run scripts/sign_code.ps1

# Create release
uv run scripts/release.py
```

## 🛡️ Security

- All network analysis runs **locally** on your machine
- No telemetry or data upload without explicit opt-in
- Data encrypted at rest with AES-256
- Minimal privilege principle for all components
- Regular security audits and updates

## 📜 License

This project is licensed under the **GNU General Public License v3.0** (GPL-3.0).

Since this project is inspired by and derived from [Portmaster](https://github.com/safing/portmaster) (GPL-3.0), we comply with GPL requirements:
- Full source code is publicly available
- All derivative works must also be GPL-3.0
- See [LICENSE](LICENSE) for full terms
- See [GPL Obligations](docs/compliance/gpl_obligations.md) for compliance details

## 🤝 Contributing

Contributions are welcome! Please read our [Developer Guide](docs/developer_guide.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Portmaster](https://github.com/safing/portmaster) by Safing - Inspiration and architectural reference
- [scikit-learn](https://scikit-learn.org/) - Machine learning foundation
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [ONNX](https://onnx.ai/) - Model interoperability

## 📞 Support

- 🐛 [Report Issues](https://github.com/yourusername/portkodiak-aishield/issues)
- 💬 [Discussions](https://github.com/yourusername/portkodiak-aishield/discussions)
- 📧 Email: support@example.com

## ⚠️ Disclaimer

This is an alpha release. Use at your own risk. Always maintain backups and test in a non-production environment first.

---

**Made with ❤️ for Privacy and Security**

