import os
import unittest
from core.vault_engine import VaultEngine

class TestVaultEngine(unittest.TestCase):
    def setUp(self):
        self.vault = VaultEngine(vault_path="test_vault.7z", temp_json="test_temp.json")
        self.master_key = "SecureTestKey123"

    def tearDown(self):
        if os.path.exists("test_vault.7z"):
            os.remove("test_vault.7z")
        if os.path.exists("test_backup.7z"):
            os.remove("test_backup.7z")

    def test_vault_operations(self):
        # ১. সেভ এবং এক্সট্র্যাক্ট টেস্ট
        test_data = [{"title": "Test", "username": "user", "password": "pass"}]
        self.vault.save_vault(self.master_key, test_data)
        
        read_data = self.vault.read_data(self.master_key)
        self.assertEqual(len(read_data), 1)
        self.assertEqual(read_data[0]["title"], "Test")

        # ২. ভুল পাসওয়ার্ড টেস্ট
        wrong_data = self.vault.read_data("WrongKey")
        self.assertIsNone(wrong_data)

        # ৩. ব্যাকআপ এবং রিস্টোর টেস্ট
        self.assertTrue(self.vault.create_backup("test_backup.7z"))
        self.assertTrue(os.path.exists("test_backup.7z"))

if __name__ == "__main__":
    unittest.main()