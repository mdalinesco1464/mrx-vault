import os
from flask import Flask, render_template, request, jsonify
from core.vault_engine import VaultEngine
from core.session_manager import SessionManager

app = Flask(__name__)
vault = VaultEngine()
session = SessionManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/unlock", methods=["POST"])
def unlock_vault():
    data = request.json
    key = data.get("master_key")
    if not key:
        return jsonify({"status": "error", "message": "Master key required"}), 400

    if vault.verify_and_extract(key):
        session.unlock(key)
        return jsonify({"status": "success", "message": "Vault unlocked successfully"})
    return jsonify({"status": "error", "message": "Invalid Master Password"}), 401

@app.route("/api/lock", methods=["POST"])
def lock_vault():
    session.lock()
    return jsonify({"status": "success", "message": "Vault locked"})

@app.route("/api/credentials", methods=["GET", "POST"])
def handle_credentials():
    if not session.is_unlocked:
        return jsonify({"status": "error", "message": "Vault is locked"}), 403

    if request.method == "GET":
        creds = vault.read_data(session.master_key)
        return jsonify({"status": "success", "data": creds if creds is not None else []})

    if request.method == "POST":
        req_data = request.json
        new_entry = req_data.get("entry")
        
        creds = vault.read_data(session.master_key)
        if creds is None:
            creds = []
        creds.append(new_entry)
        
        vault.save_vault(session.master_key, creds)
        return jsonify({"status": "success", "message": "Credential added successfully"})

@app.route("/api/backup", methods=["POST"])
def create_backup():
    if vault.create_backup():
        return jsonify({"status": "success", "message": "Encrypted backup created successfully"})
    return jsonify({"status": "error", "message": "Backup failed"}), 500

@app.route("/api/restore", methods=["POST"])
def restore_backup():
    if vault.restore_backup():
        return jsonify({"status": "success", "message": "Vault restored from backup"})
    return jsonify({"status": "error", "message": "Restore failed"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)