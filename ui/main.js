async function fetchJSON(path, opts={}){
	const token = document.getElementById('token').value.trim();
	const headers = Object.assign({'Content-Type':'application/json'}, opts.headers||{});
	if(token) headers['Authorization'] = `Bearer ${token}`;
	const res = await fetch(path, Object.assign({}, opts, {headers}));
	if(!res.ok) throw new Error(await res.text());
	return res.json();
}

async function loadTemplates(){
	try{
		const data = await fetchJSON('/api/v1/adapters/templates');
		const ul = document.getElementById('templates');
		ul.innerHTML = '';
		data.protocols.forEach(p=>{
			const li = document.createElement('li');
			const a = document.createElement('a');
			a.href = p.path; a.textContent = p.name; a.target = '_blank';
			li.appendChild(a); ul.appendChild(li);
		});
	}catch(e){ console.error(e); }
}

async function health(){
	try{
		const res = await fetchJSON('/health');
		alert('健康: ' + JSON.stringify(res));
	}catch(e){alert('失败: '+e.message)}
}

async function convert(){
	const sourceText = document.getElementById('source').value || '{}';
	const target = document.getElementById('target').value;
	let source;
	try{ source = JSON.parse(sourceText); }catch(e){ alert('JSON 无效'); return; }
	try{
		const data = await fetchJSON('/api/v1/converter/convert', {method:'POST', body: JSON.stringify({source, target})});
		document.getElementById('result').textContent = JSON.stringify(data.result, null, 2);
	}catch(e){ document.getElementById('result').textContent = e.message; }
}

async function loadTools(){
	try{
		const data = await fetchJSON('/api/v1/mcp/tools');
		document.getElementById('tools').textContent = JSON.stringify(data, null, 2);
	}catch(e){console.error(e)}
}

document.getElementById('ping').addEventListener('click', health);
window.addEventListener('load', ()=>{loadTemplates(); loadTools();});
document.getElementById('convert').addEventListener('click', convert);
