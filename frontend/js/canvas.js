export class IntersectionRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        
        this.roadWidth = 120; 
        this.laneWidth = 20; 
        
        this.centerX = this.width / 2;
        this.centerY = this.height / 2;

        this.visualVehicles = new Map();
    }

    drawStaticBackground() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.fillStyle = '#f4f7f6';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Asfalt
        this.ctx.fillStyle = '#555';
        this.ctx.fillRect(this.centerX - this.roadWidth/2, 0, this.roadWidth, this.height);
        this.ctx.fillRect(0, this.centerY - this.roadWidth/2, this.width, this.roadWidth);

        // Čiary
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;

        const drawDashedLine = (x1, y1, x2, y2) => {
            this.ctx.beginPath();
            this.ctx.setLineDash([15, 15]);
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
            this.ctx.setLineDash([]); 
        };

        const drawSolidLine = (x1, y1, x2, y2, color = 'yellow') => {
            this.ctx.beginPath();
            this.ctx.strokeStyle = color;
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
            this.ctx.strokeStyle = '#fff'; 
        };

        // Stredové čiary (žlté)
        drawSolidLine(this.centerX, 0, this.centerX, this.centerY - this.roadWidth/2); 
        drawSolidLine(this.centerX, this.centerY + this.roadWidth/2, this.centerX, this.height); 
        drawSolidLine(0, this.centerY, this.centerX - this.roadWidth/2, this.centerY); 
        drawSolidLine(this.centerX + this.roadWidth/2, this.centerY, this.width, this.centerY); 

        // Stop čiary
        this.ctx.lineWidth = 6;
        drawSolidLine(this.centerX - this.roadWidth/2, this.centerY - this.roadWidth/2, this.centerX, this.centerY - this.roadWidth/2, 'white'); 
        drawSolidLine(this.centerX, this.centerY + this.roadWidth/2, this.centerX + this.roadWidth/2, this.centerY + this.roadWidth/2, 'white'); 
        drawSolidLine(this.centerX - this.roadWidth/2, this.centerY, this.centerX - this.roadWidth/2, this.centerY + this.roadWidth/2, 'white'); 
        drawSolidLine(this.centerX + this.roadWidth/2, this.centerY - this.roadWidth/2, this.centerX + this.roadWidth/2, this.centerY, 'white'); 
        this.ctx.lineWidth = 2;

        // Prerušované čiary
        for(let i=1; i<=2; i++) {
            let offset = this.laneWidth * i;
            drawDashedLine(this.centerX - offset, 0, this.centerX - offset, this.centerY - this.roadWidth/2);
            drawDashedLine(this.centerX + offset, 0, this.centerX + offset, this.centerY - this.roadWidth/2);
            drawDashedLine(this.centerX - offset, this.centerY + this.roadWidth/2, this.centerX - offset, this.height);
            drawDashedLine(this.centerX + offset, this.centerY + this.roadWidth/2, this.centerX + offset, this.height);
            drawDashedLine(0, this.centerY - offset, this.centerX - this.roadWidth/2, this.centerY - offset);
            drawDashedLine(0, this.centerY + offset, this.centerX - this.roadWidth/2, this.centerY + offset);
            drawDashedLine(this.centerX + this.roadWidth/2, this.centerY - offset, this.width, this.centerY - offset);
            drawDashedLine(this.centerX + this.roadWidth/2, this.centerY + offset, this.width, this.centerY + offset);
        }
    }

    drawSignals(signals) {
        const drawLight = (x, y, state) => {
            this.ctx.fillStyle = '#222';
            this.ctx.fillRect(x - 8, y - 8, 16, 16);
            this.ctx.beginPath();
            this.ctx.arc(x, y, 6, 0, Math.PI * 2);
            this.ctx.fillStyle = state === 'green' ? '#0f0' : '#f00';
            this.ctx.fill();
        };

        const stopDist = this.roadWidth/2 + 15;

        // Semaformy sú teraz presne zarovnané so stredmi 3 pruhov!
        if (signals.N_L) drawLight(this.centerX - 10, this.centerY - stopDist, signals.N_L);
        if (signals.N_S) drawLight(this.centerX - 30, this.centerY - stopDist, signals.N_S);
        if (signals.N_R) drawLight(this.centerX - 50, this.centerY - stopDist, signals.N_R);

        if (signals.S_L) drawLight(this.centerX + 10, this.centerY + stopDist, signals.S_L);
        if (signals.S_S) drawLight(this.centerX + 30, this.centerY + stopDist, signals.S_S);
        if (signals.S_R) drawLight(this.centerX + 50, this.centerY + stopDist, signals.S_R);

        if (signals.E_L) drawLight(this.centerX + stopDist, this.centerY - 10, signals.E_L);
        if (signals.E_S) drawLight(this.centerX + stopDist, this.centerY - 30, signals.E_S);
        if (signals.E_R) drawLight(this.centerX + stopDist, this.centerY - 50, signals.E_R);

        if (signals.W_L) drawLight(this.centerX - stopDist, this.centerY + 10, signals.W_L);
        if (signals.W_S) drawLight(this.centerX - stopDist, this.centerY + 30, signals.W_S);
        if (signals.W_R) drawLight(this.centerX - stopDist, this.centerY + 50, signals.W_R);
    }

    drawVehicles(vehicles) {
        const carWidth = 14;
        const carLength = 24;
        const stopDist = this.roadWidth / 2 + 20;

        // Definujeme presné vektory pohybu pre radenie (žiadne desatinné odchýlky)
        const vectors = {
            'north': { dx: 0, dy: 1, angle: Math.PI / 2 },
            'south': { dx: 0, dy: -1, angle: -Math.PI / 2 },
            'east':  { dx: -1, dy: 0, angle: Math.PI },
            'west':  { dx: 1, dy: 0, angle: 0 }
        };

        const getStartPos = (dir, lane) => {
            let x, y, stopX, stopY;
            let offset = 0;
            if (lane === 'L') offset = 10;
            if (lane === 'S') offset = 30;
            if (lane === 'R') offset = 50;

            switch(dir) {
                case 'north':
                    x = this.centerX - offset; y = -50;
                    stopX = x; stopY = this.centerY - stopDist;
                    break;
                case 'south':
                    x = this.centerX + offset; y = this.height + 50;
                    stopX = x; stopY = this.centerY + stopDist;
                    break;
                case 'east':
                    x = this.width + 50; y = this.centerY - offset;
                    stopX = this.centerX + stopDist; stopY = y;
                    break;
                case 'west':
                    x = -50; y = this.centerY + offset;
                    stopX = this.centerX - stopDist; stopY = y;
                    break;
            }
            return {x, y, stopX, stopY};
        };

        const currentIds = new Set();
        const waitingCounts = {};

        // 1. Zaregistrujeme autá a vytvoríme exaktné ciele pre rad
        vehicles.forEach(v => {
            currentIds.add(v.id);
            
            if (!this.visualVehicles.has(v.id)) {
                const lane = v.lane;                
                const pos = getStartPos(v.from, lane);
                const vec = vectors[v.from];

                this.visualVehicles.set(v.id, { 
                    ...v, lane: lane,
                    x: pos.x, y: pos.y, 
                    stopX: pos.stopX, stopY: pos.stopY,
                    dx: vec.dx, dy: vec.dy, // Použijeme presný vektor pre dojazd
                    initialAngle: vec.angle, angle: vec.angle,
                    targetAngle: lane === 'L' ? vec.angle - Math.PI/2 : vec.angle + Math.PI/2,
                    color: `hsl(${Math.random() * 360}, 70%, 50%)`,
                    distanceCrossed: 0, isTurning: false, hasFinishedTurn: false
                });
            }

            const car = this.visualVehicles.get(v.id);
            car.state = 'waiting';

            const queueKey = `${v.from}_${car.lane}`;
            waitingCounts[queueKey] = (waitingCounts[queueKey] || 0);
            const queueOffset = waitingCounts[queueKey] * (carLength + 10);
            
            // Exaktný výpočet pozície v rade
            car.targetX = car.stopX - (car.dx * queueOffset);
            car.targetY = car.stopY - (car.dy * queueOffset);
            
            waitingCounts[queueKey]++;
        });

        // 2. Detekcia zelenej fázy
        for (let [id, car] of this.visualVehicles.entries()) {
            if (!currentIds.has(id)) {
                if (car.state !== 'crossing') {
                    car.state = 'crossing';
                    car.distanceCrossed = 0;
                }
            }
        }

        // 3. Pohyb a Kreslenie
        for (let [id, car] of this.visualVehicles.entries()) {
            
            if (car.state === 'waiting') {
                const speed = 10;
                const distX = car.targetX - car.x;
                const distY = car.targetY - car.y;
                
                // Pohyb pomocou exaktných celých čísel (dx a dy)
                if (Math.hypot(distX, distY) > speed) {
                    car.x += car.dx * speed;
                    car.y += car.dy * speed;
                } else {
                    car.x = car.targetX; car.y = car.targetY;
                }

            } else if (car.state === 'crossing') {
                const speed = 12;

                if (car.lane !== 'S' && !car.hasFinishedTurn) {
                    if ((car.lane === 'R' && car.distanceCrossed > 45) ||
                        (car.lane === 'L' && car.distanceCrossed > 110)) {
                        car.isTurning = true;
                    }

                    if (car.isTurning) {
                        const turnSpeed = 0.08;
                        const turnDir = car.lane === 'R' ? 1 : -1;
                        car.angle += turnSpeed * turnDir;
                        car.angleTraveled = (car.angleTraveled || 0) + turnSpeed;

                        if (car.angleTraveled >= Math.PI / 2) {
                            car.angle = car.targetAngle;
                            car.isTurning = false;
                            car.hasFinishedTurn = true;
                        }
                    }
                }

                car.distanceCrossed += speed;
                car.x += Math.cos(car.angle) * speed;
                car.y += Math.sin(car.angle) * speed;

                if (car.x < -100 || car.x > this.width + 100 || car.y < -100 || car.y > this.height + 100) {
                    this.visualVehicles.delete(id);
                    continue;
                }
            }

            this.ctx.save();
            this.ctx.translate(car.x, car.y);
            this.ctx.rotate(car.angle);

            this.ctx.fillStyle = car.color;
            this.ctx.fillRect(-carLength/2, -carWidth/2, carLength, carWidth);
            
            this.ctx.fillStyle = 'rgba(0,0,0,0.5)';
            this.ctx.fillRect(carLength/2 - 6, -carWidth/2 + 2, 4, carWidth - 4);

            this.ctx.restore();
        }
    }

    renderFrame(stateData) {
        this.drawStaticBackground();
        if (stateData.signals) this.drawSignals(stateData.signals);
        if (stateData.vehicles) this.drawVehicles(stateData.vehicles);
    }

    clearVehicles() {
    this.visualVehicles.clear();
}
}

