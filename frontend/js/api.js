const API_BASE = 'http://localhost:8000';

let _allConfigs = [], _cfgFilter = 'all';

function setFilter(f) {
  _cfgFilter = f;
  ['all','user','preset'].forEach(x => {
    const b = document.getElementById('filter-' + x);
    b.style.background   = x === f ? '#2a2a2a' : '';
    b.style.borderColor  = x === f ? '#444' : '';
    b.style.color        = x === f ? '#ccc' : '';
  });
  renderCfgList();
}

function renderCfgList() {
  const list = document.getElementById('cfg-list');
  let configs = _allConfigs;
  if(_cfgFilter === 'user')   configs = configs.filter(c => !c.is_preset);
  if(_cfgFilter === 'preset') configs = configs.filter(c =>  c.is_preset);
  if(!configs.length) {
    list.innerHTML = '<div style="font-size:12px;color:#444;padding:8px 0">Žiadne konfigurácie</div>';
    return;
  }
  list.innerHTML = configs.map(c => `
    <div style="background:#161616;border:1px solid #2a2a2a;border-radius:6px;padding:8px 10px">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
        <span style="font-size:13px;color:#ccc;font-weight:500">${c.name}${c.is_preset?'<span style="font-size:10px;color:#555;margin-left:6px">preset</span>':''}</span>
        <span style="font-size:11px;color:#555">${c.cycle_duration}s cyklus</span>
      </div>
      ${c.description ? `<div style="font-size:11px;color:#555;margin-bottom:6px">${c.description}</div>` : ''}
      <div style="display:flex;gap:4px;flex-wrap:wrap">
        <button onclick="selectCfgForSim('${c.id}')" style="font-size:11px;padding:4px 8px;background:#1a2f1a;border-color:#2a5a2a;color:#80c880">▶ Spustiť</button>
        <button onclick="editConfig('${c.id}')" style="font-size:11px;padding:4px 8px">✎ Upraviť</button>
        ${!c.is_preset ? `<button onclick="deleteConfig('${c.id}')" style="font-size:11px;padding:4px 8px;background:#2f1a1a;border-color:#5a2a2a;color:#c88080">✕ Zmazať</button>` : ''}
        <button onclick="duplicateConfig('${c.id}')" style="font-size:11px;padding:4px 8px">⧉ Duplikovať</button>
      </div>
    </div>
  `).join('');
}

async function getConfigs() {
  try {
    const r = await fetch(API_BASE + '/api/intersection/configurations');
    const d = await r.json();
    _allConfigs = Array.isArray(d) ? d : (d.configurations || []);
    renderCfgList();
  } catch(e) { console.log('Chyba:', e.message); }
}

function selectCfgForSim(cfgId) {
  document.getElementById('sim-cfg-id').value = cfgId;
  showForm('start-sim-form');
}

function editConfig(cfgId) {
  const c = _allConfigs.find(x => x.id === cfgId);
  if(!c) return;
  document.getElementById('cfg-name').value  = c.name || '';
  document.getElementById('cfg-cycle').value = c.cycle_duration || '';
  if(c.signal_timings) fillTimingsForm(c.signal_timings);
  document.getElementById('create-config-form').dataset.editId = cfgId;
  showForm('create-config-form');
}

async function duplicateConfig(cfgId) {
  const c = _allConfigs.find(x => x.id === cfgId);
  if(!c) return;
  try {
    const body = { name: c.name + ' (kópia)', description: c.description || '', cycle_duration: c.cycle_duration, signal_timings: c.signal_timings };
    await fetch(API_BASE + '/api/intersection/configurations', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    getConfigs();
  } catch(e) { console.log('Chyba:', e.message); }
}

function getTimingsFromForm() {
  const keys = ['N_S','N_L','N_R','S_S','S_L','S_R','E_S','E_L','E_R','W_S','W_L','W_R'];
  const t = {};
  for(const k of keys) {
    t[k] = {
      start:    parseInt(document.getElementById('t-'+k+'-s').value) || 0,
      duration: parseInt(document.getElementById('t-'+k+'-d').value) || 0,
    };
  }
  return t;
}

function fillTimingsForm(timings) {
  for(const [k, v] of Object.entries(timings)) {
    const s = document.getElementById('t-'+k+'-s');
    const d = document.getElementById('t-'+k+'-d');
    if(s) s.value = v.start;
    if(d) d.value = v.duration;
  }
}

function clearConfigForm() {
  document.getElementById('cfg-name').value  = '';
  document.getElementById('cfg-cycle').value = '';
  const keys = ['N_S','N_L','N_R','S_S','S_L','S_R','E_S','E_L','E_R','W_S','W_L','W_R'];
  for(const k of keys) {
    const s = document.getElementById('t-'+k+'-s');
    const d = document.getElementById('t-'+k+'-d');
    if(s) s.value = ''; if(d) d.value = '';
  }
  document.getElementById('conflict-warn').style.display = 'none';
  document.getElementById('create-config-form').dataset.editId = '';
}

async function saveConfig() {
  const editId = document.getElementById('create-config-form').dataset.editId;
  if(editId) { await updateConfig(); } else { await createConfig(); }
}

async function createConfig() {
  try {
    const body = {
      name:           document.getElementById('cfg-name').value || 'Konfigurácia',
      cycle_duration: parseInt(document.getElementById('cfg-cycle').value),
      signal_timings: getTimingsFromForm(),
    };
    const r = await fetch(API_BASE + '/api/intersection/configurations', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    const d = await r.json();
    if(d.detail && d.detail.error === 'SIGNAL_CONFLICT') {
      const w = document.getElementById('conflict-warn');
      w.style.display = 'block';
      const pairs = d.detail.conflicts.map(c => `${c.signal_a} vs ${c.signal_b} (${c.overlap_start}–${c.overlap_end}s)`).join(', ');
      w.textContent = '⚠ Konflikt semaforov: ' + pairs;
    } else if(d.detail) {
      const w = document.getElementById('conflict-warn');
      w.style.display = 'block';
      w.textContent = '⚠ Chyba: ' + (d.detail.message || JSON.stringify(d.detail));
    } else {
      document.getElementById('conflict-warn').style.display = 'none';
      clearConfigForm(); showForm('create-config-form'); getConfigs();
    }
  } catch(e) { console.log('Chyba:', e.message); }
}

async function updateConfig() {
  const cfgId = document.getElementById('create-config-form').dataset.editId;
  if(!cfgId){ alert('Nie je vybraná konfigurácia na úpravu'); return; }
  try {
    const body = {
      name:           document.getElementById('cfg-name').value || 'Konfigurácia',
      cycle_duration: parseInt(document.getElementById('cfg-cycle').value),
      signal_timings: getTimingsFromForm(),
    };
    const r = await fetch(API_BASE + '/api/intersection/configurations/' + cfgId, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    const d = await r.json();
    if(d.detail && d.detail.error === 'SIGNAL_CONFLICT') {
      const w = document.getElementById('conflict-warn');
      w.style.display = 'block';
      const pairs = d.detail.conflicts.map(c => `${c.signal_a} vs ${c.signal_b} (${c.overlap_start}–${c.overlap_end}s)`).join(', ');
      w.textContent = '⚠ Konflikt semaforov: ' + pairs;
    } else {
      document.getElementById('conflict-warn').style.display = 'none';
      clearConfigForm(); showForm('create-config-form'); getConfigs();
    }
  } catch(e) { console.log('Chyba:', e.message); }
}

async function deleteConfig(cfgId) {
  if(!cfgId) return;
  if(!confirm('Zmazať konfiguráciu?')) return;
  try {
    await fetch(API_BASE + '/api/intersection/configurations/' + cfgId, { method:'DELETE' });
    getConfigs();
  } catch(e) { console.log('Chyba:', e.message); }
}

async function startSimAPI() {
  try {
    const body = {
      config_id:           document.getElementById('sim-cfg-id').value.trim(),
      simulation_duration: parseInt(document.getElementById('sim-duration').value),
      traffic_intensity: {
        north: parseFloat(document.getElementById('sim-n').value),
        south: parseFloat(document.getElementById('sim-s').value),
        east:  parseFloat(document.getElementById('sim-e').value),
        west:  parseFloat(document.getElementById('sim-w').value),
      },
      vehicle_speed: 10,
    };
    const r = await fetch(API_BASE + '/api/intersection/simulations/start', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) });
    const d = await r.json();
    if(d.simulation_id) {
      const wsUrl = API_BASE.replace('http','ws') + '/ws/' + d.simulation_id;
      document.getElementById('wsUrl').value = wsUrl;
    }
  } catch(e) { console.log('Chyba:', e.message); }
}

async function stopSimAPI() {
  const wsUrl = document.getElementById('wsUrl').value;
  const simId = wsUrl.split('/ws/')[1];
  if(!simId) return;
  try {
    await fetch(API_BASE + '/api/intersection/simulations/' + simId, { method:'DELETE' });
    if(ws) disconnect();
    vehicles = [];
    draw();
  } catch(e) { console.log('Chyba:', e.message); }
}