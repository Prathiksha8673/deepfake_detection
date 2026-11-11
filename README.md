# DEEPFAKE X – Multimodal Synthetic Media Forensics & Authenticity Verification

![Platform Status](https://img.shields.io/badge/Status-Phase%201%20Ready-00f5d4?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.11-7928ca?style=for-the-badge)
![UI Framework](https://img.shields.io/badge/Interface-Streamlit-ff007f?style=for-the-badge)

DEEPFAKE X is an enterprise-grade digital media forensics and authenticity verification dashboard engineered for cyber-defense, open-source intelligence (OSINT), and forensic investigation teams.

---

## 🔬 Platform Capabilities

1. **AI-Generated Image Forensics**: Artifact detection, frequency spectrum analysis, metadata/EXIF consistency.
2. **Video Deepfake Detection**: Temporal frame inconsistency, facial landmark warping, audio-visual sync.
3. **Synthetic Voice Detection**: Spectrogram frequency anomalies, voice cloning fingerprinting.
4. **Document Authenticity**: Tamper detection, copy-move clone analysis, font/compression disparity.
5. **Cross-Modal Verification**: Multimodal cohesion checking (e.g. video speaker vs. speech audio track).
6. **C2PA Provenance & Cryptographic Signatures**: Content credentials and tamper inspection.
7. **Explainable AI (XAI)**: Grad-CAM attention heatmaps and transparent confidence scores.
8. **Forensic PDF Reports**: Cryptographically auditable incident reports with chain of custody.

---

## 📁 Project Architecture

```
DeepfakeX/
│
├── .venv/                   # Isolated Python 3.11 Virtual Environment
├── assets/
│   └── css/
│       └── style.css        # Dark navy/black cybersecurity UI theme
├── reports/                 # Output directory for generated forensic reports
├── src/
│   ├── components/          # Reusable UI widgets, cards, and banners
│   ├── modules/             # Forensic detection pipelines (Phase 2+)
│   └── utils/               # File parsers, metadata extractors, report builders
├── app.py                   # Main Streamlit dashboard application
├── requirements.txt         # Project package requirements
├── README.md                # System documentation
└── .gitignore               # Ignored local and runtime artifacts
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11
- `uv` Python Package Manager

### 2. Activate Virtual Environment
```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
```

### 3. Run Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
