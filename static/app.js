async function j(u,o){return (await fetch(u,o)).json()}

async function run(){
  const r = await j("/admin/run",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      agent:agent.value,
      action:action.value
    })
  });
  result.textContent = JSON.stringify(r,null,2);
  load();
}

async function approve(id,d){
  await j("/admin/approve",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({trace_id:id,decision:d})
  });
  load();
}

function row(a){
  let b="";
  if(a.status==="needs_approval"){
    b=`<button onclick="approve('${a.trace_id}','approved')">Approve</button>
       <button onclick="approve('${a.trace_id}','rejected')">Reject</button>`;
  }
  return `<div>
    ${a.agent} → ${a.action}
    <span class="${a.status==='approved'?'approved':a.status==='rejected'?'rejected':'pending'}">
      [${a.status}]
    </span>
    ${a.reason||""} ${b}
  </div>`;
}

async function load(){
  const a = await j("/admin/audit");
  audit.innerHTML = a.map(row).reverse().join("");
}

load();
