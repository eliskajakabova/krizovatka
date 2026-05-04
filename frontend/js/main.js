// --- Shared state ---
let signals = {}, vehicles = [], waitTimes = [];
let dT = 0, vid = 0, acc = {}, stats = { gen:0, pass:0 };
let localRunning = false, localTimer = null;
let mode = 'local';

const CYCLE = 60;
const TIMINGS = {
  N_S:{s:0,d:25},  N_L:{s:24,d:8},  N_R:{s:0,d:25},
  S_S:{s:0,d:25},  S_L:{s:24,d:8},  S_R:{s:0,d:25},
  E_S:{s:27,d:25}, E_L:{s:52,d:8},  E_R:{s:27,d:25},
  W_S:{s:27,d:25}, W_L:{s:52,d:8},  W_R:{s:27,d:25},
};
const INT = {
  north:{S:0.08,L:0.04,R:0.04},
  south:{S:0.08,L:0.04,R:0.04},
  east: {S:0.07,L:0.03,R:0.03},
  west: {S:0.07,L:0.03,R:0.03},
};
const SPEED = 5, DT = 100;

// --- Helpers ---
function set(id, v) { const e = document.getElementById(id); if(e) e.textContent = v; }
function showForm(id) { const el = document.getElementById(id); el.style.display = el.style.display === 'none' ? 'flex' : 'none'; }

function setDot(s) {
  const d = document.getElementById('dot'), l = document.getElementById('status-txt');
  d.className = 'dot';
  l.textContent = {connected:'Pripojený', connecting:'Pripájam…', error:'Chyba', disconnected:'Nepripojený'}[s] || s;
  if(s === 'connected') d.classList.add('on');
  if(s === 'error') d.classList.add('err');
}

function updatePills() {
  ['N_L','N_S','N_R','S_L','S_S','S_R','E_L','E_S','E_R','W_L','W_S','W_R'].forEach(k => {
    const el = document.getElementById('sig-' + k);
    if(el) el.className = 'sig ' + (signals[k] || 'red');
  });
}

// --- Local simulation ---
function getSig(ct, k) {
  const t = TIMINGS[k]; if(!t || t.d === 0) return 'red';
  const e = t.s + t.d;
  if(e <= CYCLE) return (ct >= t.s && ct < e) ? 'green' : 'red';
  return (ct >= t.s || ct < e % CYCLE) ? 'green' : 'red';
}
function sigKey(dir, lane) {
  return {north:'N', south:'S', east:'E', west:'W'}[dir] + '_' + lane;
}

function spawnVehicle(dir, lane) {
  const sp = SPAWN_PX[dir][lane], st = STOP_PX[dir][lane];
  vehicles.push({
    id:vid++, dir, lane, col:TURN_COLOR[lane]||'#4caf50',
    x:sp.x, y:sp.y, stopX:st.x, stopY:st.y,
    angle:ANGLE[dir], state:'approaching',
    waitTime:0, queueRow:0, wps:null, wpIdx:0,
  });
  stats.gen++;
}

function tick() {
  dT += DT / 1000;
  const ct = dT % CYCLE;
  if(mode !== 'ws') {
    const sigs = {};
    for(const k of Object.keys(TIMINGS)) sigs[k] = getSig(ct, k);
    signals = sigs;
  }

  for(const dir of ['north','south','east','west']) {
    for(const lane of ['S','L','R']) {
      const ak = dir + '_' + lane;
      acc[ak] = (acc[ak] || 0) + INT[dir][lane];
      while(acc[ak] >= 1){ acc[ak] -= 1; spawnVehicle(dir, lane); }
    }
  }

  const queues = {};
  for(const v of vehicles) {
    if(v.state === 'crossing' || v.state === 'done') continue;
    const k = v.dir + '_' + v.lane;
    if(!queues[k]) queues[k] = [];
    queues[k].push(v);
  }
  for(const [k, arr] of Object.entries(queues)) {
    arr.sort((a,b) => {
      const sa = STOP_PX[a.dir][a.lane];
      return Math.hypot(a.x-sa.x, a.y-sa.y) - Math.hypot(b.x-sa.x, b.y-sa.y);
    });
    arr.forEach((v,i) => v.queueRow = i);
  }

  const sigs = signals;
  const toRemove = new Set();
  for(const v of vehicles) {
    const green = sigs[sigKey(v.dir, v.lane)] === 'green';
    if(v.state === 'approaching') {
      const st = STOP_PX[v.dir][v.lane];
      const offset = v.queueRow * GAP;
      let tx = st.x, ty = st.y;
      if(v.dir==='north') ty = st.y - offset;
      else if(v.dir==='south') ty = st.y + offset;
      else if(v.dir==='east') tx = st.x + offset;
      else if(v.dir==='west') tx = st.x - offset;
      const dx = tx-v.x, dy = ty-v.y, d = Math.hypot(dx,dy);
      if(d <= SPEED) {
        v.x = tx; v.y = ty;
        if(v.queueRow === 0) {
          if(green){ v.state='crossing'; v.wps=getExitWaypoints(v.dir,v.lane); v.wpIdx=0; }
          else v.state = 'waiting';
        }
      } else { v.x += dx/d*SPEED; v.y += dy/d*SPEED; }
    }
    else if(v.state === 'waiting') {
      v.waitTime += DT / 1000;
      const st = STOP_PX[v.dir][v.lane];
      const offset = v.queueRow * GAP;
      let tx = st.x, ty = st.y;
      if(v.dir==='north') ty = st.y - offset;
      else if(v.dir==='south') ty = st.y + offset;
      else if(v.dir==='east') tx = st.x + offset;
      else if(v.dir==='west') tx = st.x - offset;
      const dx = tx-v.x, dy = ty-v.y, d = Math.hypot(dx,dy);
      if(d > 1){ v.x += dx/d*Math.min(SPEED,d); v.y += dy/d*Math.min(SPEED,d); }
      else { v.x = tx; v.y = ty; }
      if(green && v.queueRow === 0){ v.state='crossing'; v.wps=getExitWaypoints(v.dir,v.lane); v.wpIdx=0; }
    }
    else if(v.state === 'crossing') {
      if(v.wpIdx >= v.wps.length) {
        toRemove.add(v.id); stats.pass++;
        if(v.waitTime > 0) waitTimes.push(v.waitTime);
        continue;
      }
      const wp = v.wps[v.wpIdx];
      const dx = wp.x-v.x, dy = wp.y-v.y, d = Math.hypot(dx,dy);
      let da = Math.atan2(dy,dx) - v.angle;
      while(da > Math.PI) da -= 2*Math.PI;
      while(da < -Math.PI) da += 2*Math.PI;
      v.angle += da*0.18;
      if(d <= SPEED*1.5){ v.x=wp.x; v.y=wp.y; v.wpIdx++; }
      else { v.x += dx/d*SPEED*1.4; v.y += dy/d*SPEED*1.4; }
      if(v.x<-60 || v.x>W+60 || v.y<-60 || v.y>H+60) {
        toRemove.add(v.id); stats.pass++;
        if(v.waitTime > 0) waitTimes.push(v.waitTime);
      }
    }
  }
  vehicles = vehicles.filter(v => !toRemove.has(v.id));

  const waiting = vehicles.filter(v => v.state === 'waiting').length;
  const avgW = waitTimes.length ? waitTimes.reduce((a,b) => a+b, 0) / waitTimes.length : 0;
  set('st-time', ct.toFixed(1)+'s');
  set('st-gen',  stats.gen);
  set('st-pass', stats.pass);
  set('st-wait', waiting);
  set('st-avg',  avgW.toFixed(1)+'s');
  const qN = vehicles.filter(v => v.dir==='north' && v.state!=='crossing').length;
  const qS = vehicles.filter(v => v.dir==='south' && v.state!=='crossing').length;
  const qE = vehicles.filter(v => v.dir==='east'  && v.state!=='crossing').length;
  const qW = vehicles.filter(v => v.dir==='west'  && v.state!=='crossing').length;
  set('q-north', qN); set('q-south', qS); set('q-east', qE); set('q-west', qW);
  updatePills();
  draw();
}

function startLocalSim() {
  dT=0; vehicles=[]; vid=0; acc={}; waitTimes=[]; stats={gen:0,pass:0};
  if(mode !== 'ws') signals = {};
  localRunning = true;
  if(localTimer) clearInterval(localTimer);
  localTimer = setInterval(tick, DT);
}

function stopLocalSim() {
  if(localTimer){ clearInterval(localTimer); localTimer = null; }
  localRunning = false;
}

// --- Init ---
resizeCanvas();
draw();
getConfigs();