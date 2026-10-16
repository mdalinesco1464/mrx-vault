import os
import json
import platform
import subprocess

class VaultEngine:
    def __init__(self, vault_path="vault.7z", temp_json="temp_vault.json"):
        self.vault_path = vault_path
        self.temp_json = temp_json
        self.os_type = platform.system()

    def _get_7z_binary(self):
        return "7z" if self.os_type == "Windows" else "7zz"

    def verify_and_extract(self, master_key):
        """মাস্টার পাসওয়ার্ড যাচাই করে ভল্ট এক্সট্র্যাক্ট করবে"""
        binary = self._get_7z_binary()
        if not os.path.exists(self.vault_path):
            # ভল্ট ফাইল না থাকলে একটি খালি জিপ ফাইল তৈরি করে নেওয়া যেতে পারে
            self.save_vault(master_key, [])
            return True

        cmd = [binary, "x", self.vault_path, f"-p{master_key}", "-o.", self.temp_json, "-y"]
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

    def create_backup(self, backup_path="backup_vault.7z"):
        """এনক্রিপ্টেড ব্যাকআপ তৈরি করা"""
        if os.path.exists(self.vault_path):
            import shutil
            shutil.copy(self.vault_path, backup_path)
            return True
        return False

    def restore_backup(self, backup_path="backup_vault.7z"):
        """ব্যাকআপ থেকে রিস্টোর করা"""
        if os.path.exists(backup_path):
            import shutil
            shutil.copy(backup_path, self.vault_path)
            return True
        return False