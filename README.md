# 🛡️ UAAL - Universal Agent Action Layer

**The Zero-Trust Control Plane for AI Agents**

Deploy autonomous AI agents safely with enterprise-grade governance, compliance, and security controls.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🎯 What is UAAL?

UAAL is the **missing governance layer** for AI agents. It sits between your AI agents and the systems they interact with, enforcing:

✅ **Zero-Trust Access** - Least-privilege policies for every agent action  
✅ **Human-in-the-Loop** - Approval workflows for high-risk operations  
✅ **Spend Controls** - Set and enforce budget limits per agent/team  
✅ **Complete Audit Trail** - Every action logged for compliance  
✅ **Action Replay** - Simulate what-if scenarios before execution  
✅ **Instant Rollback** - Undo any agent action with one click  
✅ **Multi-Provider** - Works with OpenAI, Anthropic, Google, any LLM  

---

## 🔥 Why UAAL?

### The Problem
AI agents can now **act autonomously** across your systems - accessing databases, calling APIs, moving money, and making decisions. But:

- 🚨 80% of companies have experienced unintended AI agent actions
- 💸 No visibility into AI spending until the bill arrives
- ⚖️ Compliance teams can't audit what agents did
- 🔓 Traditional IAM doesn't cover AI agents

### The Solution
UAAL creates a **control plane** that standardizes, governs, and secures all AI agent actions - giving you:

- **Visibility**: See every action in real-time
- **Control**: Enforce policies before actions execute
- **Compliance**: Complete audit logs for SOC2, HIPAA, GDPR
- **Safety**: Rollback dangerous actions instantly

---

## 🏗️ Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   OpenAI    │     │  Anthropic  │     │   Gemini    │
│   Agents    │────▶│   Agents    │────▶│   Agents    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                   ┌───────────────┐
                   │  UAAL Control │
                   │     Plane     │
                   └───────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      [Policy       [Approval      [Audit
       Engine]       Workflow]      Logger]
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                   ┌───────────────┐
                   │  Target APIs  │
                   │   & Systems   │
                   └───────────────┘
```

---

## 🚀 Quick Start

### Installation
```bash
# Clone the repo
git clone https://github.com/LOLA0786/UAAL.git
cd UAAL

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app_v2:app --reload --port 8000
```

### Send Your First Action
```python
from agent_sdk import send_to_uaal

# Agent wants to send an email
result = send_to_uaal(
    adapter="openai_function",
    agent_output={
        "action": "send_email",
        "to": "ceo@company.com",
        "subject": "Q4 Results"
    },
    require_approval=True  # High-risk action
)

print(f"Action ID: {result['action_id']}")
print(f"Status: {result['status']}")  # "pending_approval"
```

---

## 📚 Core Features

### 1. Universal Action Schema
All agent actions are normalized to a standard format:
```json
{
  "action_id": "act_abc123",
  "agent_id": "gpt-4-analyst",
  "action_type": "api_call",
  "target": "stripe.com/v1/charges",
  "parameters": {...},
  "risk_level": "high",
  "estimated_cost": 150.00
}
```

### 2. Policy Engine
Define rules that automatically approve, block, or require human review:
```python
# Block actions over $10k
policy = {
    "rule": "block_if",
    "condition": "estimated_cost > 10000",
    "action": "require_approval"
}
```

### 3. Approval Workflows
Route high-risk actions to the right humans:
```python
# Approve via API
POST /api/v1/actions/{action_id}/approve
{
    "approver": "cfo@company.com",
    "notes": "Approved for Q4 budget"
}
```

### 4. Spend Tracking
Monitor and limit AI spending in real-time:
```python
# Set budget limits
POST /api/v1/agents/{agent_id}/budget
{
    "daily_limit": 500,
    "monthly_limit": 10000,
    "alert_threshold": 0.8
}
```

### 5. Action Replay & Simulation
Test what-if scenarios before executing:
```python
# Simulate without executing
result = replay_action(
    action_id="act_abc123",
    simulation_mode=True
)
```

### 6. Instant Rollback
Undo any action with full audit trail:
```python
# Rollback a payment
POST /api/v1/actions/{action_id}/undo
{
    "reason": "Incorrect amount",
    "undone_by": "ops@company.com"
}
```

---

## 🎯 Use Cases

### FinTech
- **Problem**: AI agent moved $50K to wrong account
- **Solution**: UAAL requires approval for transfers >$1K, maintains audit trail for compliance

### Healthcare
- **Problem**: Need HIPAA audit logs for AI accessing patient data
- **Solution**: UAAL logs every data access with timestamps, user IDs, and purposes

### E-Commerce
- **Problem**: AI agent gave 90% discount to all customers
- **Solution**: UAAL policy engine blocks discounts >50%, rollback fixed the mistake

### SaaS Platforms
- **Problem**: No visibility into which AI agent is burning through API credits
- **Solution**: UAAL tracks costs per agent, alerts when budgets are exceeded

---

## 🔌 Integrations

### Supported AI Providers
- ✅ OpenAI (GPT-4, GPT-3.5)
- ✅ Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
- ✅ Google (Gemini Pro, Gemini Ultra)
- ✅ Open-source models via API
- 🔜 AWS Bedrock
- 🔜 Azure OpenAI

### Notification Channels
- ✅ Webhooks
- 🔜 Slack
- 🔜 Microsoft Teams
- 🔜 Email
- 🔜 PagerDuty

---

## 📊 Dashboard

UAAL includes a web dashboard for monitoring and management:
```bash
# Access at http://localhost:8000/dashboard
open http://localhost:8000/dashboard
```

**Dashboard Features:**
- Real-time action feed
- Approval queue
- Spend analytics
- Anomaly alerts
- Audit log viewer

---

## 🔒 Security & Compliance

### Zero-Trust Architecture
- Every action authenticated and authorized
- Least-privilege access by default
- No ambient authority

### Audit & Compliance
- SOC 2 Type II ready (audit logs)
- HIPAA compliant data handling
- GDPR data retention policies
- Complete action replay for investigations

### Enterprise Features
- 🔜 SSO/SAML integration
- 🔜 Role-Based Access Control (RBAC)
- 🔜 Multi-tenancy
- 🔜 99.9% SLA with monitoring

---

## 🗺️ Roadmap

**Q1 2025**
- ✅ Core action standardization
- ✅ Approval workflows
- ✅ Basic policy engine
- 🚧 Spend tracking dashboard
- 🚧 Replay/simulation engine

**Q2 2025**
- [ ] SSO/SAML integration
- [ ] Advanced anomaly detection
- [ ] Slack/Teams approvals
- [ ] Multi-tenancy support

**Q3 2025**
- [ ] SOC 2 Type II certification
- [ ] GraphQL API
- [ ] Action marketplace
- [ ] Advanced analytics

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
black . && flake8 . && mypy .

# Run locally
uvicorn app_v2:app --reload
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🆚 UAAL vs. Competitors

| Feature | UAAL | Astrix ACP | Microsoft Agent 365 | LangChain |
|---------|------|------------|-------------------|-----------|
| Zero-Trust | ✅ | ✅ | ✅ | ❌ |
| Multi-Provider | ✅ | ❌ | ❌ | ✅ |
| Spend Controls | ✅ | ❌ | ❌ | ❌ |
| Action Replay | ✅ | ❌ | ❌ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ✅ |
| Approval Flows | ✅ | Limited | ✅ | ❌ |

---

## 💬 Community & Support

- **Docs**: [docs.uaal.dev](https://docs.uaal.dev) (coming soon)
- **Discord**: [Join our community](https://discord.gg/uaal) (coming soon)
- **Email**: support@uaal.dev
- **Issues**: [GitHub Issues](https://github.com/LOLA0786/UAAL/issues)

---

## 📈 Status

⚠️ **Alpha Release** - UAAL is under active development. Not recommended for production use yet.

- Current Version: 0.2.0
- Production Ready: Q2 2025 (estimated)
- Contributors: 1
- Stars: ⭐ Give us a star if this interests you!

---

## 🙏 Acknowledgments

Built with inspiration from:
- Zero-Trust security principles
- Policy-as-Code movement
- Enterprise IAM patterns
- AI safety research

---

**Made with 🛡️ by the UAAL Team**

[Website](https://uaal.dev) • [Twitter](https://twitter.com/uaal_dev) • [LinkedIn](https://linkedin.com/company/uaal)


CHANDAN GALANI,
AI ENTHUSIAST 
+91-9326176427
