async function act(agent, action) {
  const res = await fetch("/agent/action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ org: "acme", agent_id: agent, action })
  });
  const data = await res.json();

  if (action === "simulate") {
    data.note = "Dry-run only. No execution performed.";
  }

  document.getElementById("status").textContent =
    JSON.stringify(data, null, 2);

  loadAudit();
}
