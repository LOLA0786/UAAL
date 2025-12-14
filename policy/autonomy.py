class AutonomyScore:
    def __init__(self):
        self.successes = 0
        self.failures = 0

    def record_success(self):
        self.successes += 1

    def record_failure(self):
        self.failures += 1

    @property
    def score(self):
        total = self.successes + self.failures
        if total == 0:
            return 0.0
        return self.successes / total

    def allowed_without_approval(self, threshold=0.85):
        return self.score >= threshold
