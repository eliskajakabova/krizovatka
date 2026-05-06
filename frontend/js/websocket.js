let ws = null;

const LANE_MAP = {
  north:{south:'S',east:'L',west:'R'},
  south:{north:'S',west:'L',east:'R'},
  east: {west:'S',north:'L',south:'R'},
  west: {east:'S',south:'L',north:'R'},
};

function connect() {
  const url = document.getElementById('wsUrl').value.trim();
  if(!url) return;
  try{ ws = new WebSocket(url); }catch(e){ return; }
  setDot('connecting');
  ws.onopen = () => {
    mode = 'ws'; stopLocalSim(); vehicles = [];
    setDot('connected');
    document.getElementById('btnConn').style.display = 'none';
    document.getElementById('btnDisc').style.display = '';
  };
  ws.onmessage = e => { try{ handleWS(JSON.parse(e.data)); }catch{} };
  ws.onerror = () => { setDot('error'); };
  ws.onclose = () => {
    mode = 'local'; setDot('disconnected');
    document.getElementById('btnConn').style.display = '';
    document.getElementById('btnDisc').style.display = 'none';
    ws = null;
  };
}

function disconnect() { if(ws) ws.close(); }

function handleWS(msg) {
  if(msg.type === 'setup') {
    vehicles = [];
    if(!localTimer) localTimer = setInterval(() => { draw(); }, DT);
    return;
  }
  if(msg.type === 'state') {
    signals = msg.signals || {};
    const wsVehicles = msg.vehicles || [];
    const activeIds = new Set(wsVehicles.map(v => v.id));
    vehicles = vehicles.filter(v => activeIds.has(v.id) || v.state === 'crossing');
    for(const wv of wsVehicles) {
      const lane = (wv.turn) || LANE_MAP[wv.from]?.[wv.to] || 'S';
      const existing = vehicles.find(v => v.id === wv.id);
      if(!existing) {
        if(vehicles.some(v => v.id === wv.id)) continue;
        const sp = SPAWN_PX[wv.from]?.[lane];
        const st = STOP_PX[wv.from]?.[lane];
        if(!sp || !st) continue;
        vehicles.push({
          id:wv.id, dir:wv.from, lane, col:TURN_COLOR[lane]||'#4caf50',
          x:sp.x, y:sp.y, stopX:st.x, stopY:st.y,
          angle:ANGLE[wv.from], state:wv.state, queueRow:0, wps:null, wpIdx:0,
        });
      } else {
        if(existing.state !== 'crossing' && wv.state === 'crossing') {
          existing.wps = getExitWaypoints(existing.dir, existing.lane);
          existing.wpIdx = 0;
          existing.committed = false;
        }
        existing.state = wv.state;
      }
    }
    const queues = {};
    for(const v of vehicles) {
      if(v.state === 'crossing' && v.committed) continue;
      const k = v.dir + '_' + v.lane;
      if(!queues[k]) queues[k] = [];
      queues[k].push(v);
    }
    for(const [k, arr] of Object.entries(queues)) {
      arr.sort((a,b) => { const sa = STOP_PX[a.dir][a.lane]; return Math.hypot(a.x-sa.x,a.y-sa.y) - Math.hypot(b.x-sa.x,b.y-sa.y); });
      arr.forEach((v,i) => v.queueRow = i);
    }
    const toRemove = new Set();
    for(const v of vehicles) {
      if(v.state === 'crossing') {
        if(!v.wps){ v.wps = getExitWaypoints(v.dir, v.lane); v.wpIdx = 0; }
        if(!v.committed && v.x > CX-RW/2 && v.x < CX+RW/2 && v.y > CY-RW/2 && v.y < CY+RW/2) {
          v.committed = true;
        }
        if(!v.committed && signals[sigKey(v.dir, v.lane)] !== 'green') {
          const st = STOP_PX[v.dir][v.lane];
          const offset = v.queueRow * GAP;
          let tx = st.x, ty = st.y;
          if(v.dir==='north') ty = st.y - offset;
          else if(v.dir==='south') ty = st.y + offset;
          else if(v.dir==='east') tx = st.x + offset;
          else if(v.dir==='west') tx = st.x - offset;
          const dx = tx-v.x, dy = ty-v.y, d = Math.hypot(dx,dy);
          if(d > SPEED){ v.x += dx/d*SPEED; v.y += dy/d*SPEED; }
          else{ v.x = tx; v.y = ty; }
          continue;
        }
        if(v.wpIdx >= v.wps.length){ toRemove.add(v.id); continue; }
        const wp = v.wps[v.wpIdx];
        const dx = wp.x-v.x, dy = wp.y-v.y, d = Math.hypot(dx,dy);
        let da = Math.atan2(dy,dx) - v.angle;
        while(da > Math.PI) da -= 2*Math.PI;
        while(da < -Math.PI) da += 2*Math.PI;
        v.angle += da*0.18;
        if(d <= SPEED*1.5){ v.x=wp.x; v.y=wp.y; v.wpIdx++; }
        else{ v.x += dx/d*SPEED*1.4; v.y += dy/d*SPEED*1.4; }
        if(v.x<-60 || v.x>W+60 || v.y<-60 || v.y>H+60) toRemove.add(v.id);
      } else {
        const st = STOP_PX[v.dir][v.lane];
        const offset = v.queueRow * GAP;
        let tx = st.x, ty = st.y;
        if(v.dir==='north') ty = st.y - offset;
        else if(v.dir==='south') ty = st.y + offset;
        else if(v.dir==='east') tx = st.x + offset;
        else if(v.dir==='west') tx = st.x - offset;
        const dx = tx-v.x, dy = ty-v.y, d = Math.hypot(dx,dy);
        if(d > SPEED){ v.x += dx/d*SPEED; v.y += dy/d*SPEED; }
        else{ v.x = tx; v.y = ty; }
      }
    }
    vehicles = vehicles.filter(v => !toRemove.has(v.id));
    const q = msg.queue_lengths || {}, s = msg.statistics || {};
    set('q-north', q.north??'—'); set('q-south', q.south??'—');
    set('q-east',  q.east??'—');  set('q-west',  q.west??'—');
    set('st-time', msg.time != null ? msg.time.toFixed(1)+'s' : '—');
    set('st-gen',  s.total_vehicles_generated??'—');
    set('st-pass', s.total_vehicles_passed??'—');
    set('st-wait', s.total_vehicles_waiting??'—');
    set('st-avg',  s.average_wait_time != null ? s.average_wait_time.toFixed(1)+'s' : '—');
    updatePills(); draw(); return;
  }
  if(msg.type === 'completed') {
    if(localTimer){ clearInterval(localTimer); localTimer = null; }
    vehicles = []; signals = {}; updatePills();
    const f = msg.final_statistics || {};
    set('st-gen',  f.total_vehicles_generated??'—');
    set('st-pass', f.total_vehicles_passed??'—');
    set('st-avg',  f.average_wait_time != null ? f.average_wait_time.toFixed(1)+'s' : '—');
    draw();
  }
}