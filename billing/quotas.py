class Quota:
    def __init__(self, max_actions):
        self.max_actions = max_actions
        self.used = 0

    def consume(self):
        if self.used >= self.max_actions:
            raise PermissionError("Quota exceeded")
        self.used += 1
