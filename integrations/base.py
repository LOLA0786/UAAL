class IntegrationBase:
    """
    Base class. All integrations should override only the verbs they support.
    Workers call these methods dynamically.
    """

    # --- Universal Verbs (UAAL standard) ---

    def create_event(self, **kwargs):
        raise NotImplementedError("create_event not implemented")

    def send_message(self, **kwargs):
        raise NotImplementedError("send_message not implemented")

    def create_document(self, **kwargs):
        raise NotImplementedError("create_document not implemented")

    def update_record(self, **kwargs):
        raise NotImplementedError("update_record not implemented")

    def delete_record(self, **kwargs):
        raise NotImplementedError("delete_record not implemented")

    # --- Undo / Compensation ---

    def undo_create_event(self, **kwargs):
        pass

    def undo_send_message(self, **kwargs):
        pass

    def undo_create_document(self, **kwargs):
        pass
