class ExecutionContext:
    def __init__(self, user, api_key, session):
        self.user = user
        self.api_key = api_key
        self.session = session

        self.spend_limit = api_key.spend_limit
        self.max_batch_size = api_key.max_batch_size or 50
        self.min_confidence = 0.6
        self.consent = session.consent

    def is_anomalous(self, intent):
        return False
