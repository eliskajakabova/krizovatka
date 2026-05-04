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

    _getTurnTarget(from, lane) {
        const map = {
            north: {
                L: { to: 'west', lane: 'L' },
                S: { to: 'south', lane: 'S' },
                R: { to: 'east', lane: 'R' },
            },
            south: {
                L: { to: 'east', lane: 'L' },
                S: { to: 'north', lane: 'S' },
                R: { to: 'west', lane: 'R' },
            },
            east: {
                L: { to: 'north', lane: 'L' },
                S: { to: 'west', lane: 'S' },
                R: { to: 'south', lane: 'R' },
            },
            west: {
                L: { to: 'south', lane: 'L' },
                S: { to: 'east', lane: 'S' },
                R: { to: 'north', lane: 'R' },
            },
        };

        return map[from][lane];
    }

    drawStaticBackground() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.fillStyle = '#f4f7f6';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // asfalt
        this.ctx.fillStyle = '#555';
        this.ctx.fillRect(
            this.centerX - this.roadWidth / 2,
            0,
            this.roadWidth,
            this.height
        );
        this.ctx.fillRect(
            0,
            this.centerY - this.roadWidth / 2,
            this.width,
            this.roadWidth
        );

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

        const drawSolidLine = (x1, y1, x2, y2, color = 'yellow', width = 2) => {
            const prevStroke = this.ctx.strokeStyle;
            const prevWidth = this.ctx.lineWidth;

            this.ctx.beginPath();
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = width;
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();

            this.ctx.strokeStyle = prevStroke;
            this.ctx.lineWidth = prevWidth;
        };

        // žlté stredové čiary
        drawSolidLine(
            this.centerX,
            0,
            this.centerX,
            this.centerY - this.roadWidth / 2,
            'yellow',
            2
        );
        drawSolidLine(
            this.centerX,
            this.centerY + this.roadWidth / 2,
            this.centerX,
            this.height,
            'yellow',
            2
        );
        drawSolidLine(
            0,
            this.centerY,
            this.centerX - this.roadWidth / 2,
            this.centerY,
            'yellow',
            2
        );
        drawSolidLine(
            this.centerX + this.roadWidth / 2,
            this.centerY,
            this.width,
            this.centerY,
            'yellow',
            2
        );

        // stop čiary
        drawSolidLine(
            this.centerX - this.roadWidth / 2,
            this.centerY - this.roadWidth / 2,
            this.centerX,
            this.centerY - this.roadWidth / 2,
            'white',
            6
        );
        drawSolidLine(
            this.centerX,
            this.centerY + this.roadWidth / 2,
            this.centerX + this.roadWidth / 2,
            this.centerY + this.roadWidth / 2,
            'white',
            6
        );
        drawSolidLine(
            this.centerX - this.roadWidth / 2,
            this.centerY,
            this.centerX - this.roadWidth / 2,
            this.centerY + this.roadWidth / 2,
            'white',
            6
        );
        drawSolidLine(
            this.centerX + this.roadWidth / 2,
            this.centerY - this.roadWidth / 2,
            this.centerX + this.roadWidth / 2,
            this.centerY,
            'white',
            6
        );

        // 3 pruhy v každom smere
        for (let i = 1; i <= 2; i++) {
            const offset = this.laneWidth * i;

            // horná vetva
            drawDashedLine(
                this.centerX - offset,
                0,
                this.centerX - offset,
                this.centerY - this.roadWidth / 2
            );
            drawDashedLine(
                this.centerX + offset,
                0,
                this.centerX + offset,
                this.centerY - this.roadWidth / 2
            );

            // dolná vetva
            drawDashedLine(
                this.centerX - offset,
                this.centerY + this.roadWidth / 2,
                this.centerX - offset,
                this.height
            );
            drawDashedLine(
                this.centerX + offset,
                this.centerY + this.roadWidth / 2,
                this.centerX + offset,
                this.height
            );

            // ľavá vetva
            drawDashedLine(
                0,
                this.centerY - offset,
                this.centerX - this.roadWidth / 2,
                this.centerY - offset
            );
            drawDashedLine(
                0,
                this.centerY + offset,
                this.centerX - this.roadWidth / 2,
                this.centerY + offset
            );

            // pravá vetva
            drawDashedLine(
                this.centerX + this.roadWidth / 2,
                this.centerY - offset,
                this.width,
                this.centerY - offset
            );
            drawDashedLine(
                this.centerX + this.roadWidth / 2,
                this.centerY + offset,
                this.width,
                this.centerY + offset
            );
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

        const stopDist = this.roadWidth / 2 + 2;

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

    _getLaneCenters(direction, isOutgoing = false) {
        const w = this.laneWidth; // 20
        // Offsety od stredu: 10, 30, 50 px
        // Prichádzajúce: -50 (R), -30 (S), -10 (L)
        // Odchádzajúce:  10 (L),  30 (S),  50 (R)
        
        const incoming = { L: -10, S: -30, R: -50 };
        const outgoing = { L: 10, S: 30, R: 50 };
        const offsets = isOutgoing ? outgoing : incoming;

        switch (direction) {
            case 'north': return { L: this.centerX + offsets.L, S: this.centerX + offsets.S, R: this.centerX + offsets.R };
            case 'south': return { L: this.centerX - offsets.L, S: this.centerX - offsets.S, R: this.centerX - offsets.R };
            case 'east':  return { L: this.centerY - offsets.L, S: this.centerY - offsets.S, R: this.centerY - offsets.R };
            case 'west':  return { L: this.centerY + offsets.L, S: this.centerY + offsets.S, R: this.centerY + offsets.R };
        }
    }

    _getVehicleTemplate(direction, lane) {
        const stopDist = this.roadWidth / 2 + 20;
        const lanes = this._getLaneCenters(direction);
        const laneCenter = lanes[lane] ?? lanes.S;

        switch (direction) {
            case 'north':
                return {
                    x: laneCenter,
                    y: -50,
                    stopX: laneCenter,
                    stopY: this.centerY - stopDist,
                    angle: Math.PI / 2,
                };
            case 'south':
                return {
                    x: laneCenter,
                    y: this.height + 50,
                    stopX: laneCenter,
                    stopY: this.centerY + stopDist,
                    angle: -Math.PI / 2,
                };
            case 'east':
                return {
                    x: this.width + 50,
                    y: laneCenter,
                    stopX: this.centerX + stopDist,
                    stopY: laneCenter,
                    angle: Math.PI,
                };
            case 'west':
                return {
                    x: -50,
                    y: laneCenter,
                    stopX: this.centerX - stopDist,
                    stopY: laneCenter,
                    angle: 0,
                };
            default:
                return {
                    x: 0,
                    y: 0,
                    stopX: 0,
                    stopY: 0,
                    angle: 0,
                };
        }
    }

    _getWaitingTargetByLane(direction, lane, rowIndex, gap) {
        const stopDist = this.roadWidth / 2 + 20;
        const lanes = this._getLaneCenters(direction);
        const laneCenter = lanes[lane] ?? lanes.S;

        switch (direction) {
            case 'north':
                return {
                    x: laneCenter,
                    y: this.centerY - stopDist - rowIndex * gap,
                };
            case 'south':
                return {
                    x: laneCenter,
                    y: this.centerY + stopDist + rowIndex * gap,
                };
            case 'east':
                return {
                    x: this.centerX + stopDist + rowIndex * gap,
                    y: laneCenter,
                };
            case 'west':
                return {
                    x: this.centerX - stopDist - rowIndex * gap,
                    y: laneCenter,
                };
            default:
                return {
                    x: 0,
                    y: 0,
                };
        }
    }

    _moveTowards(vehicle, targetX, targetY, speed) {
        const dx = targetX - vehicle.x;
        const dy = targetY - vehicle.y;
        const dist = Math.hypot(dx, dy);

        if (dist <= speed) {
            vehicle.x = targetX;
            vehicle.y = targetY;
            return;
        }

        vehicle.x += (dx / dist) * speed;
        vehicle.y += (dy / dist) * speed;
    }
    _isVertical(direction) {
        return direction === 'north' || direction === 'south';
    }

    _startLocalCrossing(vehicle) {
        if (vehicle.localCrossingStarted) {
            return;
        }

        const lanes = this._getLaneCenters(vehicle.from);
        const laneCenter = lanes[vehicle.lane] ?? lanes.S;

        if (vehicle.from === 'north' || vehicle.from === 'south') {
            vehicle.lockedAxis = laneCenter;
            vehicle.x = laneCenter;
        } else {
            vehicle.lockedAxis = laneCenter;
            vehicle.y = laneCenter;
        }

        vehicle.localCrossingStarted = true;
        vehicle.localCrossingDistance = 0;
    }

    _isCarInFront(vehicle) {
        const safeDistance = 45; // dĺžka auta (24) + rezerva

        for (const other of this.visualVehicles.values()) {
            if (vehicle.id === other.id) continue;
            if (vehicle.from !== other.from || vehicle.lane !== other.lane) continue;
            if (vehicle.renderState !== other.renderState) continue;

            const dx = other.x - vehicle.x;
            const dy = other.y - vehicle.y;

            // Kontrola podľa smeru jazdy
            if (vehicle.from === 'north' && dy > 0 && dy < safeDistance) return true;
            if (vehicle.from === 'south' && dy < 0 && dy > -safeDistance) return true;
            if (vehicle.from === 'east' && dx < 0 && dx > -safeDistance) return true;
            if (vehicle.from === 'west' && dx > 0 && dx < safeDistance) return true;
        }
        return false;
    }

    _updateLocalCrossing(vehicle) {
    const speed = 5;
    const maxDistance = Math.max(this.width, this.height);
    this._startLocalCrossing(vehicle);

    const lanes = this._getLaneCenters(vehicle.from);
    const centerPoint = this.roadWidth / 2; // Bod, kde sa cesty krížia

    // Pomocná logika pre smer po otočení
    if (vehicle.lane === 'S') {
        // ROVNO - tvoja pôvodná logika
        if (vehicle.from === 'north') vehicle.y += speed;
        if (vehicle.from === 'south') vehicle.y -= speed;
        if (vehicle.from === 'east')  vehicle.x -= speed;
        if (vehicle.from === 'west')  vehicle.x += speed;
    } else {
        
        this._handleTurning(vehicle, speed);
    }

    vehicle.localCrossingDistance += speed;
    return vehicle.localCrossingDistance <= maxDistance;
}

    _handleTurning(vehicle, speed) {
        // Získame stredy pruhov cesty, KAM auto ide (isOutgoing = true)
        const targetLanes = this._getLaneCenters(vehicle.to, true);
        const targetPos = targetLanes[vehicle.targetLane];

        // Bod zlomu (pivot) - stred križovatky s malým posunom podľa pruhu
        const pivotX = this.centerX;
        const pivotY = this.centerY;

        let reachedPivot = false;
        if (vehicle.from === 'north') reachedPivot = vehicle.y >= pivotY + (vehicle.lane === 'L' ? -10 : 10);
        if (vehicle.from === 'south') reachedPivot = vehicle.y <= pivotY + (vehicle.lane === 'L' ? 10 : -10);
        if (vehicle.from === 'east')  reachedPivot = vehicle.x <= pivotX + (vehicle.lane === 'L' ? 10 : -10);
        if (vehicle.from === 'west')  reachedPivot = vehicle.x >= pivotX + (vehicle.lane === 'L' ? -10 : 10);

        if (!reachedPivot) {
            // Ešte sme neprišli do stredu -> pokračuj rovno
            if (vehicle.from === 'north') vehicle.y += speed;
            if (vehicle.from === 'south') vehicle.y -= speed;
            if (vehicle.from === 'east')  vehicle.x -= speed;
            if (vehicle.from === 'west')  vehicle.x += speed;
        } else {
            // Už točíme -> nastavíme cieľovú os a uhol
            if (vehicle.to === 'north' || vehicle.to === 'south') {
                vehicle.x = targetPos; // Zarovnaj sa na pruh novej cesty
                if (vehicle.to === 'north') { vehicle.y -= speed; vehicle.angle = -Math.PI/2; }
                else { vehicle.y += speed; vehicle.angle = Math.PI/2; }
            } else {
                vehicle.y = targetPos; // Zarovnaj sa na pruh novej cesty
                if (vehicle.to === 'east') { vehicle.x += speed; vehicle.angle = 0; }
                else { vehicle.x -= speed; vehicle.angle = Math.PI; }
            }
        }
    }

    drawVehicles(vehicles) {
        const carWidth = 14;
        const carLength = 24;
        const gap = carLength + 15;
        const currentIds = new Set();

        const laneQueues = {
            north: { L: [], S: [], R: [] },
            south: { L: [], S: [], R: [] },
            east: { L: [], S: [], R: [] },
            west: { L: [], S: [], R: [] },
        };

        vehicles.forEach((vehicle) => {
            currentIds.add(vehicle.id);

            const direction = (vehicle.from || 'north').toLowerCase();
            const lane = (vehicle.lane || 'S').toUpperCase();
            const backendState = (vehicle.state || 'waiting').toLowerCase();

            if (!this.visualVehicles.has(vehicle.id)) {
                const template = this._getVehicleTemplate(direction, lane);
                const target = this._getTurnTarget(direction, lane);

                this.visualVehicles.set(vehicle.id, {
                    id: vehicle.id,
                    from: direction,
                    lane,
                    to: target.to,
                    targetLane: target.lane,
                    backendState,
                    renderState: 'waiting',
                    wait_time: vehicle.wait_time || 0,
                    x: template.x,
                    y: template.y,
                    stopX: template.stopX,
                    stopY: template.stopY,
                    angle: template.angle,
                    lockedAxis: null,
                    localCrossingStarted: false,
                    localCrossingDistance: 0,
                    color: `hsl(${Math.random() * 360}, 70%, 50%)`,
                });
            }

            const visual = this.visualVehicles.get(vehicle.id);
            if (backendState === 'crossing' && visual.renderState !== 'crossing') {
                visual.renderState = 'crossing';
                visual.localCrossingStarted = false; // Resetni pre istotu
            }

            visual.from = direction;
            visual.lane = lane;
            visual.backendState = backendState;
            visual.wait_time = vehicle.wait_time || 0;

            if (visual.renderState === 'waiting') {
                laneQueues[direction][lane].push(visual);
            }
        });

        for (const [id, vehicle] of this.visualVehicles.entries()) {
            if (!currentIds.has(id)) {
                if (vehicle.renderState === 'crossing') {
                    continue; 
                }
                vehicle.missingFrames = (vehicle.missingFrames || 0) + 1;

                if (vehicle.missingFrames > 10) {
                    this.visualVehicles.delete(id);
                }
            } else {
                vehicle.missingFrames = 0;
            }
        }

        for (const direction of ['north', 'south', 'east', 'west']) {
            for (const lane of ['L', 'S', 'R']) {
                const queue = laneQueues[direction][lane];

                queue.sort((a, b) => {
                    switch (direction) {
                        case 'north':
                            return b.y - a.y;
                        case 'south':
                            return a.y - b.y;
                        case 'east':
                            return a.x - b.x;
                        case 'west':
                            return b.x - a.x;
                        default:
                            return 0;
                    }
                });

                queue.forEach((vehicle, rowIndex) => {
                    const target = this._getWaitingTargetByLane(direction, lane, rowIndex, gap);
                    
                    if (!this._isCarInFront(vehicle)) {
                        this._moveTowards(vehicle, target.x, target.y, 8);
                    }
                });
            }
        }

        for (const vehicle of this.visualVehicles.values()) {
            if (vehicle.renderState !== 'waiting') {
                continue;
            }

            const isCrossing = vehicle.backendState === 'crossing';

            if (isCrossing && vehicle.renderState !== 'crossing') {
                vehicle.renderState = 'crossing';
                vehicle.localCrossingStarted = false;
                vehicle.localCrossingDistance = 0;
            } 
        }

        for (const [id, vehicle] of this.visualVehicles.entries()) {
            if (vehicle.renderState !== 'crossing') {
                continue;
            }

            const keep = this._updateLocalCrossing(vehicle);
            if (!keep) {
                vehicle.outOfBounds = (vehicle.outOfBounds || 0) + 1;

                if (vehicle.outOfBounds > 30) {
                    vehicle.finished = true;
                }
            } else {
                vehicle.outOfBounds = 0;
            }
        }

        for (const vehicle of this.visualVehicles.values()) {
            this.ctx.save();
            this.ctx.translate(vehicle.x, vehicle.y);
            this.ctx.rotate(vehicle.angle);

            this.ctx.fillStyle = vehicle.color;
            this.ctx.fillRect(
                -carLength / 2,
                -carWidth / 2,
                carLength,
                carWidth
            );

            this.ctx.fillStyle = 'rgba(0,0,0,0.5)';
            this.ctx.fillRect(
                carLength / 2 - 6,
                -carWidth / 2 + 2,
                4,
                carWidth - 4
            );

            this.ctx.restore();
        }
        for (const [id, vehicle] of this.visualVehicles.entries()) {
            if (vehicle.finished && vehicle.missingFrames > 5) {
                this.visualVehicles.delete(id);
            }
        }
    }

    renderFrame(stateData) {
        this.drawStaticBackground();

        if (stateData.signals) {
            this.drawSignals(stateData.signals);
        }

        if (stateData.vehicles) {
            this.drawVehicles(stateData.vehicles);
        }
    }

    clearVehicles() {
        this.visualVehicles.clear();
    }
}
