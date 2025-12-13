import requests
import os
from integrations.base import IntegrationBase


class SlackReal(IntegrationBase):
    TOKEN = os.getenv("SLACK_BOT_TOKEN", "")

    def send_message(self, channel: str, text: str, **kwargs):
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {self.TOKEN}"}

        resp = requests.post(url, headers=headers, json={
            "channel": channel,
            "text": text
        })

        return resp.json()
