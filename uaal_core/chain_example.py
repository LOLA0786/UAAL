from uaal import authorize, link_decision

parent = authorize(
    agent="billing-agent",
    action="generate_invoice",
    payload={"amount": 1200}
)

child = authorize(
    agent="email-agent",
    action="send_invoice",
    payload={"invoice_id": "INV-91"}
)

link_decision(parent.id, child.id)
