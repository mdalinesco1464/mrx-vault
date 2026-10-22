import os
from flask import Flask, render_template, request, jsonify
from core.vault_engine import VaultEngine
from core.session_manager import SessionManager
import random, string

app = Flask(__name__)
vault = VaultEngine()
session = SessionManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/api/unlock', methods=['POST'])
def unlock_vault():
    data = request.get_json()
    master_key = data.get('master_key')
    
    if vault.verify_and_extract(master_key):
        session.unlock(master_key)
        return jsonify({"success": True})
        
    return jsonify({"success": False, "message": "Invalid Master Password!"}), 400

@app.route('/api/lock', methods=['POST'])
def lock_vault():
    session.lock()
    return jsonify({"success": True})

@app.route("/api/credentials", methods=["GET", "POST", "DELETE"])
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

    if request.method == "DELETE":
        req_data = request.json
        index_to_delete = req_data.get("index")
        
        creds = vault.read_data(session.master_key)
        if creds is not None and 0 <= index_to_delete < len(creds):
            creds.pop(index_to_delete)
            vault.save_vault(session.master_key, creds)
            return jsonify({"status": "success", "message": "Credential deleted successfully"})
        
        return jsonify({"status": "error", "message": "Invalid index or credential not found"}), 400

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


# --- ব্রাউজার এক্সটেনশনের জন্য নতুন API এন্ডপয়েন্টসমূহ ---

@app.route('/api/ext/generate', methods=['GET'])
def ext_generate_credential():
    """নির্দিষ্ট পলিসি অনুযায়ী স্ট্রং পাসওয়ার্ড এবং প্রি-সেট ইমেইল রিটার্ন করবে"""
    
    
    preferred_emails = [
        "younusalicmt08@gmail.com",
        "mdabu7109@gmail.com",
        "mdalinesco1464@gmail.com"
    ]
    
    # পাসওয়ার্ড পলিসি নিশ্চিত করার জন্য ক্যারেক্টার সেট
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # বাধ্যতামূলকভাবে প্রতি ক্যাটাগরি থেকে অন্তত একটি করে ক্যারেক্টার নেওয়া
    password_chars = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]
    
    # বাকি অক্ষরগুলো মিলিয়ে মোট দৈর্ঘ্য ১২ বা তার বেশি করা (কমপক্ষে ৮)
    all_chars = lower + upper + digits + special
    for _ in range(10): # মোট দৈর্ঘ্য ১৪ হবে
        password_chars.append(random.choice(all_chars))
        
    # পাসওয়ার্ডের অক্ষরগুলোকে র্যান্ডমভাবে এলোমেলো করা (Shuffle)
    random.shuffle(password_chars)
    strong_pass = ''.join(password_chars)
    
    return jsonify({
        "success": True,
        "emails": preferred_emails,
        "password": strong_pass
    })
    preferred_emails = [
        "younusalicmt08@gmail.com",
        "mdabu7109@gmail.com",
        "mdalinesco1464@gmail.com"
    ]

@app.route('/api/ext/save', methods=['POST'])
def ext_save_credential():
    """এক্সটেনশন থেকে সাইন-আপের পর ক্রেডেনশিয়াল সেভ করা"""
    if not session.is_unlocked:
        return jsonify({"success": False, "message": "Vault is locked. Please unlock first."}), 403
        
    req_data = request.json
    new_entry = {
        "title": req_data.get('title'),
        "username": req_data.get('username'),
        "password": req_data.get('password')
    }
    
    creds = vault.read_data(session.master_key) or []
    creds.append(new_entry)
    vault.save_vault(session.master_key, creds)
    
    return jsonify({"success": True, "message": "Saved to MRX-Vault!"})

@app.route('/api/ext/get', methods=['POST'])
def ext_get_credential():
    """সাইন-িনের সময় ডোমেইন অনুযায়ী পাসওয়ার্ড খুঁজে বের করা"""
    if not session.is_unlocked:
        return jsonify({"success": False, "message": "Vault is locked."}), 403
        
    req_data = request.json
    site_title = req_data.get('title')
    
    creds = vault.read_data(session.master_key) or []
    for item in creds:
        if site_title in item.get('title', ''):
            return jsonify({
                "success": True,
                "username": item.get('username'),
                "password": item.get('password')
            })
            
    return jsonify({"success": False, "message": "No credential found for this site."})



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)