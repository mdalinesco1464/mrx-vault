import threading
import time

class SecurityManager:
    @staticmethod
    def setup_clipboard_expiry(clipboard_func, clear_func, delay=10):
        """১০ সেকেন্ড পর ক্লিপবোর্ড খালি করার ব্যাকগ্রাউন্ড থ্রেড"""
        def clear_task():
            time.sleep(delay)
            clear_func()

        thread = threading.Thread(target=clear_task)
        thread.daemon = True
        thread.start()