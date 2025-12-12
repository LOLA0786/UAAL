const fetch = require("node-fetch");

class UAALClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl.replace(/\\/$/, "");
    this.apiKey = apiKey;
  }
  _headers() {
    const h = { "Content-Type": "application/json" };
    if (this.apiKey) h["x-api-key"] = this.apiKey;
    return h;
  }
  async sendAction(adapter, agentOutput, requireApproval=false) {
    const res = await fetch(`${this.baseUrl}/api/v1/actions`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ adapter, agent_output: agentOutput, require_approval: requireApproval }),
    });
    return res.json();
  }
}
module.exports = { UAALClient };
