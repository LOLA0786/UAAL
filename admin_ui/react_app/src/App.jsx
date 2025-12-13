import React, {useEffect, useState} from "react";

const BASE = "http://127.0.0.1:8000";

function fetchWithKey(path) {
  const key = localStorage.getItem("uaal_key") || "";
  return fetch(BASE + path, {headers: {"x-api-key": key}}).then(r=>r.json());
}

export default function App(){
  const [policies, setPolicies] = useState([]);
  const [actions, setActions] = useState([]);
  const [selectedAction, setSelectedAction] = useState(null);
  const [audit, setAudit] = useState(null);

  useEffect(()=>{ load(); }, []);

  async function load(){
    try{
      const p = await fetchWithKey("/admin/policies");
      setPolicies(p||[]);
      const a = await fetchWithKey("/api/v1/actions?limit=50");
      setActions(a||[]);
    }catch(e){ console.error(e) }
  }

  async function showAudit(id){
    setSelectedAction(id);
    const res = await fetchWithKey("/api/v1/audit/action/" + id);
    setAudit(res);
  }

  async function savePolicy(){
    const raw = document.getElementById("policy").value;
    let payload;
    try { payload = JSON.parse(raw); } catch(e){ alert("invalid json"); return; }
    const key = localStorage.getItem("uaal_key") || "";
    const r = await fetch(BASE + "/admin/policies", {method:"POST", headers: {"Content-Type":"application/json","x-api-key": key}, body: JSON.stringify(payload)});
    const j = await r.json();
    alert(JSON.stringify(j));
    load();
  }

  return (
    <div style={{display:"flex", gap:20, padding:20}}>
      <div style={{flex:1}}>
        <h2>Policies</h2>
        <textarea id="policy" style={{width:"100%",height:200}} defaultValue={JSON.stringify({
          "name":"Block large purchase",
          "rules":[{"field":"intent","op":"eq","value":"purchase"},{"field":"parameters.amount","op":"gt","value":1000,"action":"block","require_2fa":true}]
        },null,2)} />
        <button onClick={savePolicy}>Save Policy</button>
        <pre>{JSON.stringify(policies,null,2)}</pre>
      </div>
      <div style={{flex:1}}>
        <h2>Recent Actions</h2>
        <ul>
          {actions.map(a=>(
            <li key={a.action_id}>
              <b>{a.actor_id}</b> - {a.verb} - {a.state} - <button onClick={()=>showAudit(a.action_id)}>Audit</button>
            </li>
          ))}
        </ul>
      </div>
      <div style={{flex:1}}>
        <h2>Audit</h2>
        <pre>{audit ? JSON.stringify(audit,null,2) : "Select action to view audit"}</pre>
      </div>
    </div>
  );
}
