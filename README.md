# 🔒 MRX-VAULT
A lightweight, self-hosted, zero-trust local password manager built with **Python Flask**, **7-Zip (AES-256)**, **PowerShell & Bash Scripts**, and **Git**.

## Features
- **Master Password with Vault Lock & Unlock:** Secure access control with session-based persistence.
- **Credential Management:** Add, search, and securely copy credentials with a 10-second clipboard auto-expiry timer.
- **Auto-Capture & Auto-Fill:** Automatically captures credentials during sign-up and seamlessly auto-fills them on   subsequent logins.
- **Encrypted Backups:** Create and restore AES-256 encrypted backups via 7-Zip integration.

## Prerequisites & Dependencies 
- **Python 3.x** and Flask framework with a virtual environment.
- **7-Zip binaries (`7z.exe` & `7z.dll`)** included in the project root directory for handling AES-256 encrypted backups.
- **Git** installed on your system.

---

## 🚀 Installation & Setup Guide
```bash
mkdir -p vault
cd vault
```
-**For Windows 
```bash
python -m venv .venv
.venv\Scripts\Activate
-**For Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

###  Clone the Repository
```bash
git clone https://github.com/mdalinesco1464/mrx-vault.git
cd mrx-vault 
```
### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python app.py
```

### Open browser
and type (http://127.0.0.1:5000/)