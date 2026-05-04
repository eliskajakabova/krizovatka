const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const W = 500, H = 500, CX = W/2, CY = H/2;
const RW = 120, LW = 20;
const STOP_DIST = RW/2 + 20;
let SCALE = 1;

function resizeCanvas() {
  const wrap = document.getElementById('canvas-wrap');
  const sz = Math.min(wrap.clientWidth, wrap.clientHeight) - 20;
  canvas.width  = sz;
  canvas.height = sz;
  SCALE = sz / 500;
}
window.addEventListener('resize', () => { resizeCanvas(); draw(); });

const LANE_PX = {
  north:{L:CX-10, S:CX-30, R:CX-50},
  south:{L:CX+10, S:CX+30, R:CX+50},
  east: {L:CY-10, S:CY-30, R:CY-50},
  west: {L:CY+10, S:CY+30, R:CY+50},
};

const SPAWN_PX = {
  north:{L:{x:CX-10,y:-30},  S:{x:CX-30,y:-30},  R:{x:CX-50,y:-30}},
  south:{L:{x:CX+10,y:H+30}, S:{x:CX+30,y:H+30}, R:{x:CX+50,y:H+30}},
  east: {L:{x:W+30,y:CY-10}, S:{x:W+30,y:CY-30}, R:{x:W+30,y:CY-50}},
  west: {L:{x:-30,y:CY+10},  S:{x:-30,y:CY+30},  R:{x:-30,y:CY+50}},
};

const STOP_PX = {
  north:{L:{x:CX-10,y:CY-STOP_DIST}, S:{x:CX-30,y:CY-STOP_DIST}, R:{x:CX-50,y:CY-STOP_DIST}},
  south:{L:{x:CX+10,y:CY+STOP_DIST}, S:{x:CX+30,y:CY+STOP_DIST}, R:{x:CX+50,y:CY+STOP_DIST}},
  east: {L:{x:CX+STOP_DIST,y:CY-10}, S:{x:CX+STOP_DIST,y:CY-30}, R:{x:CX+STOP_DIST,y:CY-50}},
  west: {L:{x:CX-STOP_DIST,y:CY+10}, S:{x:CX-STOP_DIST,y:CY+30}, R:{x:CX-STOP_DIST,y:CY+50}},
};

const ANGLE = {north:Math.PI/2, south:-Math.PI/2, east:Math.PI, west:0};
const CAR_L = 24, CAR_W = 14, GAP = CAR_L + 15;
const TURN_COLOR = {L:'#5b8dd9', S:'#4caf50', R:'#e67e22'};

function getExitWaypoints(dir, lane) {
  const sd = STOP_DIST;
  if(dir==='north'){
    if(lane==='R') return [{x:CX-50,y:CY-50},{x:-60,y:CY-50}];
    if(lane==='S') return [{x:CX-30,y:CY+sd+40},{x:CX-30,y:H+60}];
    if(lane==='L') return [{x:CX-10,y:CY},{x:CX,y:CY+10},{x:W+60,y:CY+10}];
  }
  if(dir==='south'){
    if(lane==='R') return [{x:CX+50,y:CY+50},{x:W+60,y:CY+50}];
    if(lane==='S') return [{x:CX+30,y:CY-sd-40},{x:CX+30,y:-60}];
    if(lane==='L') return [{x:CX+10,y:CY},{x:CX,y:CY-10},{x:-60,y:CY-10}];
  }
  if(dir==='east'){
    if(lane==='R') return [{x:CX+50,y:CY-50},{x:CX+50,y:-60}];
    if(lane==='S') return [{x:CX-sd-40,y:CY-30},{x:-60,y:CY-30}];
    if(lane==='L') return [{x:CX,y:CY-10},{x:CX-10,y:CY},{x:CX-10,y:H+60}];
  }
  if(dir==='west'){
    if(lane==='R') return [{x:CX-50,y:CY+50},{x:CX-50,y:H+60}];
    if(lane==='S') return [{x:CX+sd+40,y:CY+30},{x:W+60,y:CY+30}];
    if(lane==='L') return [{x:CX,y:CY+10},{x:CX+10,y:CY},{x:CX+10,y:-60}];
  }
  return [{x:CX,y:CY}];
}

function drawBackground(){
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#f4f7f6'; ctx.fillRect(0,0,W,H);
  ctx.fillStyle='#555';
  ctx.fillRect(CX-RW/2,0,RW,H);
  ctx.fillRect(0,CY-RW/2,W,RW);
  const dashLine=(x1,y1,x2,y2)=>{
    ctx.beginPath();ctx.setLineDash([15,15]);
    ctx.strokeStyle='#fff';ctx.lineWidth=2;
    ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
    ctx.setLineDash([]);
  };
  const solidLine=(x1,y1,x2,y2,col,w)=>{
    ctx.beginPath();ctx.strokeStyle=col;ctx.lineWidth=w;
    ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
  };
  solidLine(CX,0,CX,CY-RW/2,'yellow',2);
  solidLine(CX,CY+RW/2,CX,H,'yellow',2);
  solidLine(0,CY,CX-RW/2,CY,'yellow',2);
  solidLine(CX+RW/2,CY,W,CY,'yellow',2);
  solidLine(CX-RW/2,CY-RW/2,CX,CY-RW/2,'white',6);
  solidLine(CX,CY+RW/2,CX+RW/2,CY+RW/2,'white',6);
  solidLine(CX-RW/2,CY,CX-RW/2,CY+RW/2,'white',6);
  solidLine(CX+RW/2,CY-RW/2,CX+RW/2,CY,'white',6);
  for(let i=1;i<=2;i++){
    const o=LW*i;
    dashLine(CX-o,0,CX-o,CY-RW/2); dashLine(CX+o,0,CX+o,CY-RW/2);
    dashLine(CX-o,CY+RW/2,CX-o,H); dashLine(CX+o,CY+RW/2,CX+o,H);
    dashLine(0,CY-o,CX-RW/2,CY-o); dashLine(0,CY+o,CX-RW/2,CY+o);
    dashLine(CX+RW/2,CY-o,W,CY-o); dashLine(CX+RW/2,CY+o,W,CY+o);
  }
}

function drawSignals(){
  const sd=STOP_DIST+25;
  const lights=[
    {x:CX-10,y:CY-sd,k:'N_L'},{x:CX-30,y:CY-sd,k:'N_S'},{x:CX-50,y:CY-sd,k:'N_R'},
    {x:CX+10,y:CY+sd,k:'S_L'},{x:CX+30,y:CY+sd,k:'S_S'},{x:CX+50,y:CY+sd,k:'S_R'},
    {x:CX+sd,y:CY-10,k:'E_L'},{x:CX+sd,y:CY-30,k:'E_S'},{x:CX+sd,y:CY-50,k:'E_R'},
    {x:CX-sd,y:CY+10,k:'W_L'},{x:CX-sd,y:CY+30,k:'W_S'},{x:CX-sd,y:CY+50,k:'W_R'},
  ];
  for(const l of lights){
    const g=signals[l.k]==='green';
    const isE=l.k.startsWith('E'),isW=l.k.startsWith('W'),isN=l.k.startsWith('N');
    const swap=isN||isE;
    ctx.fillStyle='#111'; ctx.beginPath();
    if(isE||isW){
      ctx.roundRect(l.x-14,l.y-7,28,14,3); ctx.fill();
      ctx.beginPath(); ctx.arc(l.x-6,l.y,5,0,Math.PI*2);
      ctx.fillStyle=swap?(g?'#440000':'#ff2222'):(g?'#00cc44':'#003300'); ctx.fill();
      ctx.beginPath(); ctx.arc(l.x+6,l.y,5,0,Math.PI*2);
      ctx.fillStyle=swap?(g?'#00cc44':'#003300'):(g?'#440000':'#ff2222'); ctx.fill();
    }else{
      ctx.roundRect(l.x-7,l.y-14,14,28,3); ctx.fill();
      ctx.beginPath(); ctx.arc(l.x,l.y-6,5,0,Math.PI*2);
      ctx.fillStyle=swap?(g?'#00cc44':'#003300'):(g?'#440000':'#ff2222'); ctx.fill();
      ctx.beginPath(); ctx.arc(l.x,l.y+6,5,0,Math.PI*2);
      ctx.fillStyle=swap?(g?'#440000':'#ff2222'):(g?'#00cc44':'#003300'); ctx.fill();
    }
  }
}

function drawVehicles(){
  for(const v of vehicles){
    ctx.save();
    ctx.translate(v.x,v.y);
    ctx.rotate(v.angle);
    ctx.fillStyle=v.col;
    ctx.fillRect(-CAR_L/2,-CAR_W/2,CAR_L,CAR_W);
    ctx.fillStyle='rgba(0,0,0,0.5)';
    ctx.fillRect(CAR_L/2-6,-CAR_W/2+2,4,CAR_W-4);
    if(v.state==='waiting'){
      ctx.strokeStyle='#e74c3c'; ctx.lineWidth=2;
      ctx.strokeRect(-CAR_L/2-1,-CAR_W/2-1,CAR_L+2,CAR_W+2);
    }
    ctx.restore();
  }
}

function draw(){
  ctx.save();
  ctx.scale(SCALE,SCALE);
  drawBackground();
  drawVehicles();
  drawSignals();
  ctx.restore();
}