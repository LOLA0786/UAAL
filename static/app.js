function act(agent, action) {
  fetch("/agent/action", {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({ org:"acme", agent_id:agent, action })
  })
  .then(r=>r.json())
  .then(d=>document.getElementById("status").textContent=JSON.stringify(d,null,2));
}

fetch("/agent/graph")
  .then(r=>r.json())
  .then(g=>document.getElementById("graph").textContent=JSON.stringify(g,null,2));

fetch("/agent/policy/acme")
  .then(r=>r.json())
  .then(p=>document.getElementById("policy").textContent=JSON.stringify(p,null,2));

fetch("/agent/soc2")
  .then(r=>r.json())
  .then(s=>document.getElementById("soc2").textContent=JSON.stringify(s,null,2));
