from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>UAAL Demo Dashboard</title>
  <style>
    body { font-family: Arial; margin: 40px; }
    h2 { margin-top: 40px; }
    button { padding: 6px 12px; margin: 6px 6px 6px 0; }
    input { padding: 6px; margin: 4px; }
    pre { background: #f4f4f4; padding: 10px; }
    .ok { color: green; font-weight: bold; }
    .err { color: red; font-weight: bold; }
    .box { border: 1px solid #ddd; padding: 15px; margin-top: 10px; }
  </style>
</head>
<body>

<h1>UAAL – Live Authorization Demo</h1>

<h2>1️⃣ Create Agent</h2>
<input id="owner" value="agent1"/>
<input id="scopes" value="read"/>
<br/>
<button onclick="createAgent()">Create Agent</button>
<pre id="createResult"></pre>

<h2>2️⃣ Agent Actions</h2>
<div class="box">
  <button onclick="agentRead()">Read</button>
  <button onclick="agentExecute()">Execute</button>
  <button onclick="sendPayment()">Send Payment</button>
  <pre id="actionResult"></pre>
</div>

<h2>3️⃣ Registry / Audit</h2>
<button onclick="loadAudit()">Refresh</button>
<pre id="auditLog"></pre>

<script>
let API_KEY = null;

function show(el, text, ok=true) {
  const node = document.getElementById(el);
  node.className = ok ? "ok" : "err";
  node.textContent = text;
}

async function safeFetch(url, options={}) {
  try {
    const r = await fetch(url, options);
    const t = await r.text();
    return { status: r.status, body: t };
  } catch (e) {
    return { status: "NETWORK_ERROR", body: e.toString() };
  }
}

async function createAgent() {
  const res = await safeFetch('/admin/api-keys/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': 'super-secret-admin-key'
    },
    body: JSON.stringify({
      owner: document.getElementById('owner').value,
      role: 'agent',
      scopes: document.getElementById('scopes').value.split(','),
      policy: { allowed_hours: [9,18] }
    })
  });

  show('createResult', res.body, res.status === 200);

  try {
    const j = JSON.parse(res.body);
    API_KEY = j.api_key;
  } catch {}
}

async function agentRead() {
  if (!API_KEY) {
    show('actionResult', 'No agent key yet', false);
    return;
  }
  const res = await safeFetch('/agent/read', {
    headers: { 'x-api-key': API_KEY }
  });
  show('actionResult', res.body, res.status === 200);
}

async function agentExecute() {
  if (!API_KEY) {
    show('actionResult', 'No agent key yet', false);
    return;
  }
  const res = await safeFetch('/agent/execute', {
    method: 'POST',
    headers: { 'x-api-key': API_KEY }
  });
  show('actionResult', res.body, false);
}

function sendPayment() {
  show('actionResult',
    'BLOCKED: payments require explicit permission',
    false
  );
}

async function loadAudit() {
  const res = await safeFetch('/admin/api-keys/audit');
  show('auditLog', res.body, true);
}
</script>

</body>
</html>
"""
