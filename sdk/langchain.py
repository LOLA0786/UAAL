class UAALTool:
    def __init__(self, client):
        self.client = client

    def run(self, action):
        return self.client.send_action(action)
