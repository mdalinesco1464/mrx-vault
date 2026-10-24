import os
from flask import Flask, render_template, request, jsonify
from core.vault_engine import VaultEngine
from core.session_manager import SessionManager
import random, string
from dotenv import load_dotenv

app = Flask(__name__)
vault = VaultEngine()
session = SessionManager()

# .env ফাইল থেকে ভ্যারিয়েবল লোড নিশ্চিত করার জন্য
load_dotenv()

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
        
        if not new_entry or not new_entry.get("title") or not new_entry.get("password"):
            return jsonify({"status": "error", "message": "Title and password are required"}), 400

        creds = vault.read_data(session.master_key)
        if creds is None:
            creds = []
        
        new_title = new_entry.get("title", "").strip().lower()
        new_user = new_entry.get("username", "").strip().lower()
        
        # ডুপ্লিকেট চেক ও রেস্ট্রিক্ট করার লজিক
        for item in creds:
            if item.get("title", "").strip().lower() == new_title and item.get("username", "").strip().lower() == new_user:
                return jsonify({
                    "status": "error", 
                    "message": "Duplicate Entry! This title and username already exist in your vault."
                }), 400
        
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
    """নির্দিষ্ট পলিসি অনুযায়ী স্ট্রং পাসওয়ার্ড এবং প্রি-সেট ইমেইল রিটার্ন করবে"""
    
    # .env ফাইল থেকে PREFERRED_EMAILS রিড করা (কমা দিয়ে আলাদা করা ইমেইল)
    raw_emails = os.getenv("PREFERRED_EMAILS", "")
    preferred_emails = [email.strip() for email in raw_emails.split(",") if email.strip()]
    
    # পাসওয়ার্ড পলিসি নিশ্চিত করার জন্য ক্যারেক্টার সেট
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # বাধ্যতামূলকভাবে প্রতি ক্যাটাগরি থেকে অন্তত একটি করে ক্যারেক্টার নেওয়া
    password_chars = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]
    
    # বাকি অক্ষরগুলো মিলিয়ে মোট দৈর্ঘ্য ১৪ করা
    all_chars = lower + upper + digits + special
    for _ in range(10): 
        password_chars.append(random.choice(all_chars))
        
    # পাসওয়ার্ডের অক্ষরগুলোকে র্যান্ডমভাবে এলোমেলো করা (Shuffle)
    random.shuffle(password_chars)
    strong_pass = ''.join(password_chars)
    
    return jsonify({
        "success": True,
        "emails": preferred_emails,
        "password": strong_pass
    })

@app.route('/api/ext/save', methods=['POST'])
def ext_save_credential():
    """এক্সটেনশন থেকে সাইন-আপ বা লগইনের পর ক্রেডেনশিয়াল ডুপ্লিকেট ছাড়া সেভ করা"""
    if not session.is_unlocked:
        return jsonify({"success": False, "message": "Vault is locked. Please unlock first."}), 403
        
    req_data = request.json
    new_title = req_data.get('title')
    new_user = req_data.get('username')
    new_pass = req_data.get('password')

    if not new_title or not new_pass:
        return jsonify({"success": False, "message": "Invalid data received."}), 400

    creds = vault.read_data(session.master_key) or []
    
    # ১. চেক করা যে একই ডোমেন এবং ইউজারনেমের এন্ট্রি আগে থেকেই আছে কি না
    for item in creds:
        if item.get('title') == new_title and item.get('username') == new_user:
            # যদি পাসওয়ার্ড পরিবর্তন হয়ে থাকে তবে আপডেট করে দেওয়া
            if item.get('password') != new_pass:
                item['password'] = new_pass
                vault.save_vault(session.master_key, creds)
                return jsonify({"success": True, "message": "Password updated in MRX-Vault!"})
            # যদি পাসওয়ার্ডও একই থাকে তবে ডুপ্লিকেট না বানিয়ে ফেরত পাঠানো
            return jsonify({"success": True, "message": "Credential already exists!"})

    # ২. ডুপ্লিকেট না থাকলে নতুন এন্ট্রি যুক্ত করা
    new_entry = {
        "title": new_title,
        "username": new_user,
        "password": new_pass
    }
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
@app.route('/api/ext/match', methods=['POST'])
def ext_match_credential():
    """ডোমেইন অনুযায়ী ভল্ট থেকে পাসওয়ার্ড ও ইউজারনেম খুঁজে বের করা"""
    if not session.is_unlocked:
        return jsonify({"success": False, "message": "Vault locked"}), 403

    domain = request.json.get('domain', '').lower()
    creds = vault.read_data(session.master_key) or []

    # ডোমেইন নাম ম্যাচ করানো (যেমন: example.com)
    matched = []
    for item in creds:
        title = item.get('title', '').lower()
        if domain in title or title in domain:
            matched.append(item)

    if matched:
        return jsonify({"success": True, "found": True, "credentials": matched})
    else:
        return jsonify({"success": True, "found": False})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)