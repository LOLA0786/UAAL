from integrations.base import IntegrationBase


class NotionFake(IntegrationBase):
    def create_document(self, title: str, **kwargs):
        print(f"[FAKE NOTION] create_document: {title}")
        return {"fake": True, "doc_created": True}

    def update_record(self, record_id: str, fields: dict, **kwargs):
        print(f"[FAKE NOTION] update_record: {record_id}")
        return {"fake": True, "updated": True}
