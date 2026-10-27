PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>ZT Broker</title>
<style>
:root{--bg:#1a1714;--card:#262220;--line:#3a332e;--text:#ece6dd;--mute:#9a9086;--amber:#d98b2b;--red:#d1495b;--green:#7fa650}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:"Segoe UI",Arial,sans-serif;padding:28px}
h1{font-family:Georgia,serif;font-weight:600;margin:0 0 4px}
.sub{color:var(--mute);margin-bottom:22px}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 18px;min-width:150px}
.card b{display:block;font-size:28px;font-family:Georgia,serif}
.card span{color:var(--mute);font-size:12px;text-transform:uppercase;letter-spacing:.08em}
table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:8px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);font-size:13px;vertical-align:top}
th{color:var(--mute);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.08em}
td{font-family:Consolas,"Cascadia Mono",monospace}
.bad{color:var(--red)} .ok{color:var(--green)} .warn{color:var(--amber)}
</style></head><body>
<h1>Credential Broker</h1>
<div class="sub">Live audit trail. Refreshes every 2 seconds.</div>
<div class="cards">
<div class="card"><b id="c_issued">0</b><span>Tokens issued</span></div>
<div class="card"><b id="c_revoked">0</b><span>Revoked</span></div>
<div class="card"><b id="c_deny">0</b><span>Denied</span></div>
<div class="card"><b id="c_decoy">0</b><span>Decoys issued</span></div>
<div class="card"><b id="c_hit">0</b><span>Decoy hits</span></div>
</div>
<table><thead><tr><th>Time</th><th>Event</th><th>Details</th></tr></thead><tbody id="rows"></tbody></table>
<script>
function td(t,c){var d=document.createElement('td');d.textContent=t;if(c)d.className=c;return d;}
async function load(){
  var r=await fetch('/v1/audit'); var rows=await r.json();
  var c={issued:0,revoked:0,deny:0,decoy:0,hit:0};
  var tb=document.getElementById('rows'); tb.innerHTML='';
  rows.slice().reverse().forEach(function(e){
    var cls='';
    if(e.event==='token_issued')c.issued++;
    if(e.event==='revoked'){c.revoked++;cls='ok';}
    if(e.event==='decision'&&e.outcome==='deny'){c.deny++;cls='bad';}
    if(e.event==='DECOY_ISSUED'){c.decoy++;cls='warn';}
    if(e.event==='DECOY_HIT'){c.hit++;cls='bad';}
    var rest=Object.assign({},e); delete rest.ts; delete rest.event;
    var tr=document.createElement('tr');
    tr.appendChild(td(new Date(e.ts*1000).toLocaleTimeString()));
    tr.appendChild(td(e.event,cls));
    tr.appendChild(td(JSON.stringify(rest)));
    tb.appendChild(tr);
  });
  for(var k in c){document.getElementById('c_'+k).textContent=c[k];}
}
load(); setInterval(load,2000);
</script></body></html>"""