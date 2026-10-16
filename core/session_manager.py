class SessionManager:
    def __init__(self):
        self._master_key = None
        self._is_unlocked = False

    def unlock(self, master_key):
        self._master_key = master_key
        self._is_unlocked = True

    def lock(self):
        self._master_key = None
        self._is_unlocked = False

    @property
    def is_unlocked(self):
        return self._is_unlocked

    @property
    def master_key(self):
        return self._master_key