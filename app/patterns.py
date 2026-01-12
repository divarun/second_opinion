import json
from pathlib import Path

class FailurePatternLibrary:
    def __init__(self, path: str):
        self.patterns = json.loads(Path(path).read_text())

    def all(self):
        return self.patterns
