#vault_engine.py
import os
import json
import platform
import subprocess
import shutil
from dotenv import load_dotenv

# .env ফাইল লোড করা
load_dotenv()

class VaultEngine:
    def __init__(self, vault_filename="vault.7z", backup_filename="backup_vault.7z", temp_json="temp_vault.json"):
        # .env থেকে পাথ নেওয়া, না থাকলে ডিফল্ট ইউজার হোম ফোল্ডারে .vault ব্যবহার করা
        default_dir = os.path.join(os.path.expanduser("~"), ".vault")
        self.vault_dir = os.getenv("VAULT_DIR_PATH", default_dir)
        
        # ডিরেক্টরি না থাকলে তৈরি করে নেওয়া এবং উইন্ডোজে হিডেন (+h) করে দেওয়া
        if not os.path.exists(self.vault_dir):
            os.makedirs(self.vault_dir)
            if platform.system() == "Windows":
                os.system(f'attrib +h "{self.vault_dir}"')

        # ফুল ফাইল পাথগুলো ডিক্লেয়ার করা
        self.vault_path = os.path.join(self.vault_dir, vault_filename)
        self.backup_path = os.path.join(self.vault_dir, backup_filename)
        self.temp_json = os.path.join(self.vault_dir, temp_json)
        
        self.os_type = platform.system()

    def _get_7z_binary(self):
        return "7z" if self.os_type == "Windows" else "7zz"

    def verify_and_extract(self, master_key):
        """মাস্টার পাসওয়ার্ড যাচাই করে ভল্ট এক্সট্র্যাক্ট করবে"""
        binary = self._get_7z_binary()
        if not os.path.exists(self.vault_path):
            # ভল্ট ফাইল না থাকলে একটি খালি ভল্ট তৈরি করে নেওয়া
            self.save_vault(master_key, [])
            return True

        # -o দিয়ে নির্দিষ্ট আউটপুট ফোল্ডার বা ফাইল পাথ সেট করা
        cmd = [binary, "x", self.vault_path, f"-p{master_key}", f"-o{self.vault_dir}", os.path.basename(self.temp_json), "-y"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return res.returncode == 0
        except subprocess.CalledProcessError:
            return False

    def read_data(self, master_key):
        if self.verify_and_extract(master_key):
            try:
                if os.path.exists(self.temp_json):
                    with open(self.temp_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data
            finally:
                if os.path.exists(self.temp_json):
                    os.remove(self.temp_json)
        return None

    def save_vault(self, master_key, data_list):
        binary = self._get_7z_binary()
        with open(self.temp_json, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4)

        cmd = [binary, "a", self.vault_path, self.temp_json, f"-p{master_key}", "-mhe=on", "-y"]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        finally:
            if os.path.exists(self.temp_json):
                os.remove(self.temp_json)

    def create_backup(self):
        """এনক্রিপ্টেড ব্যাকআপ তৈরি করা"""
        if os.path.exists(self.vault_path):
            shutil.copy(self.vault_path, self.backup_path)
            return True
        return False

    def restore_backup(self):
        """ব্যাকআপ থেকে রিস্টোর করা"""
        if os.path.exists(self.backup_path):
            shutil.copy(self.backup_path, self.vault_path)
            return True
        return False