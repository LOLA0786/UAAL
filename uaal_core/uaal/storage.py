import os, json

class EvidenceStore:
    def write(self, key: str, data: dict):
        raise NotImplementedError

class LocalStore(EvidenceStore):
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), "evidence")
        os.makedirs(self.base_dir, exist_ok=True)

    def write(self, key: str, data: dict):
        path = os.path.join(self.base_dir, key)
        if os.path.exists(path):
            raise RuntimeError("Immutable write violation")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
