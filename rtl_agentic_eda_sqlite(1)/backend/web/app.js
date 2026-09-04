const steps=['planning','rtl','testbench','simulation','synthesis','sta','physical_design','physical_verification'];
const labels={planning:'Planning',rtl:'RTL generation',testbench:'Cocotb generation',simulation:'Simulation',synthesis:'Synthesis',sta:'OpenSTA',physical_design:'Physical design',physical_verification:'Physical verification'};
let events=[],job=null,art={rtl:'',tb:'',report:''};
const $=x=>document.getElementById(x);

function render(){
  let last={}; events.forEach(e=>{if(e.step)last[e.step]=e});
  let done=0;
  $('steps').innerHTML=steps.map(s=>{
    let e=last[s],c='',t='Pending';
    if(e?.type==='step_started'){c='run';t='Running · attempt '+(e.attempt||1)}
    if(e?.status==='passed'){c='pass';t='Passed · '+(e.attempt||1)+' attempt(s)';done++}
    if(e?.type==='step_failed'){c='fail';t='Failed · attempt '+(e.attempt||1)}
    return `<div class="step ${c}"><b>${labels[s]}</b><div class="state">${t}</div></div>`
  }).join('');
  $('progress').textContent=`${done} / 8`;
  $('agent').innerHTML=events.slice(-40).reverse().map(e=>`<div class="event"><b>${e.type.replaceAll('_',' ')}</b><small>${e.step||e.diagnosis?.diagnosis||e.error||e.status||''}</small></div>`).join('');
  $('logs').textContent=events.filter(e=>e.output||e.error).map(e=>`[${e.step||'pipeline'}] ${e.output||e.error}`).join('\n\n');
}

async function load(path,key){
  if(!job)return;
  let r=await fetch(`/api/design/${job}/artifact?path=${encodeURIComponent(path)}`);
  if(r.ok){art[key]=await r.text();show(document.querySelector('.tab.active').dataset.tab)}
}
function show(k){$('artifact').textContent=art[k]||'Waiting for artifact...'}

async function loadJob(id){
  const r=await fetch(`/api/design/${id}`);
  if(!r.ok)return;
  const d=await r.json();
  job=id; events=[]; art={rtl:'',tb:'',report:''};
  $('prompt').value=d.prompt||''; $('job').textContent='Job '+id;
  $('status').className='badge '+(d.status==='completed'?'completed':d.status==='failed'?'failed':'running');
  $('status').textContent=d.status.toUpperCase();
  if(d.plan)events.push({type:'state_snapshot',status:d.status});
  Object.entries(d.steps||{}).forEach(([step,v])=>{
    events.push({type:'step_'+(v.status==='passed'?'completed':v.status==='failed'?'failed':'started'),step,status:v.status,attempt:v.attempts,output:v.output,error:v.error});
  });
  render();
  await load('rtl/design.sv','rtl');
  await load('testbench/test_design.py','tb');
  art.report=JSON.stringify(d.report||{},null,2);
  show(document.querySelector('.tab.active').dataset.tab);
  connectWebSocket(id);
}

function connectWebSocket(id){
  const protocol=location.protocol==='https:'?'wss':'ws';
  const ws=new WebSocket(`${protocol}://${location.host}/ws/${id}`);
  ws.onmessage=async m=>{
    const e=JSON.parse(m.data);
    if(e.type==='state_snapshot'){
      if(e.status){
        $('status').className='badge '+(e.status==='completed'?'completed':e.status==='failed'?'failed':'running');
        $('status').textContent=e.status.toUpperCase();
      }
      return;
    }
    if(e.type==='job_not_found')return;
    events.push(e); render();
    if(e.type==='pipeline_completed'||e.type==='pipeline_failed'){
      $('status').className='badge '+(e.type==='pipeline_completed'?'completed':'failed');
      $('status').textContent=e.type==='pipeline_completed'?'COMPLETED':'FAILED';
      await load('rtl/design.sv','rtl'); await load('testbench/test_design.py','tb');
      art.report=JSON.stringify(e.report||{},null,2); show(document.querySelector('.tab.active').dataset.tab); $('run').disabled=false; loadHistory();
    }
  };
  ws.onerror=()=>{ $('status').className='badge failed'; $('status').textContent='WS ERROR'; };
}

async function loadHistory(){
  const r=await fetch('/api/designs');
  if(!r.ok)return;
  const d=await r.json();
  $('history').innerHTML=(d.jobs||[]).map(x=>`<button class="history-btn" data-id="${x.job_id}">${x.status.toUpperCase()} · ${new Date(x.updated_at).toLocaleString()} · ${escapeHtml(x.prompt.slice(0,80))}</button>`).join('')||'<span>No saved runs yet.</span>';
  document.querySelectorAll('.history-btn').forEach(b=>b.onclick=()=>loadJob(b.dataset.id));
}
function escapeHtml(s){return s.replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}

$('run').onclick=async()=>{
  $('run').disabled=true; events=[]; art={rtl:'',tb:'',report:''}; $('status').className='badge running'; $('status').textContent='RUNNING';
  let r=await fetch('/api/design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:$('prompt').value})});
  let d=await r.json(); job=d.job_id; $('job').textContent='Job '+job; connectWebSocket(job); loadHistory();
};
$('refreshJobs').onclick=loadHistory;
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');show(b.dataset.tab)});
render(); show('rtl'); loadHistory();
