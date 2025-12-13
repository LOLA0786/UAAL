from integrations.base import IntegrationBase


class NotionReal(IntegrationBase):
    """
    Placeholder for real Notion API using official SDK.
    """

    def create_document(self, title: str, **kwargs):
        raise NotImplementedError("Configure Notion API token")

    def update_record(self, record_id: str, fields: dict, **kwargs):
        raise NotImplementedError("Configure Notion API token")
