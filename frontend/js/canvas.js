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

        const stopDist = this.roadWidth / 2 + 15;

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

    _getLaneCenters(direction) {
        switch (direction) {
            case 'north':
                return {
                    L: this.centerX - 10,
                    S: this.centerX - 30,
                    R: this.centerX - 50,
                };
            case 'south':
                return {
                    L: this.centerX + 10,
                    S: this.centerX + 30,
                    R: this.centerX + 50,
                };
            case 'east':
                return {
                    L: this.centerY - 10,
                    S: this.centerY - 30,
                    R: this.centerY - 50,
                };
            case 'west':
                return {
                    L: this.centerY + 10,
                    S: this.centerY + 30,
                    R: this.centerY + 50,
                };
            default:
                return {
                    L: 0,
                    S: 0,
                    R: 0,
                };
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

    _updateLocalCrossing(vehicle) {
        const speed = 10;
        const maxDistance = this.roadWidth + 40;

        this._startLocalCrossing(vehicle);

        switch (vehicle.from) {
            case 'north':
                vehicle.x = vehicle.lockedAxis;
                vehicle.y += speed;
                break;
            case 'south':
                vehicle.x = vehicle.lockedAxis;
                vehicle.y -= speed;
                break;
            case 'east':
                vehicle.y = vehicle.lockedAxis;
                vehicle.x -= speed;
                break;
            case 'west':
                vehicle.y = vehicle.lockedAxis;
                vehicle.x += speed;
                break;
        }

        vehicle.localCrossingDistance += speed;
        return vehicle.localCrossingDistance <= maxDistance;
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
            const backendState = vehicle.state || 'waiting';

            if (!this.visualVehicles.has(vehicle.id)) {
                const template = this._getVehicleTemplate(direction, lane);

                this.visualVehicles.set(vehicle.id, {
                    id: vehicle.id,
                    from: direction,
                    lane,
                    backendState,
                    renderState: backendState === 'crossing' ? 'crossing' : 'waiting',
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
            if (!visual) {
                return;
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
            if (currentIds.has(id)) {
                continue;
            }

            if (vehicle.renderState === 'waiting') {
                this.visualVehicles.delete(id);
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
                    const target = this._getWaitingTargetByLane(
                        direction,
                        lane,
                        rowIndex,
                        gap
                    );
                    this._moveTowards(vehicle, target.x, target.y, 8);
                });
            }
        }

        for (const vehicle of this.visualVehicles.values()) {
            if (vehicle.renderState !== 'waiting') {
                continue;
            }

            if (vehicle.backendState !== 'crossing') {
                continue;
            }

            const nearStopLine =
                Math.abs(vehicle.x - vehicle.stopX) <= 12 &&
                Math.abs(vehicle.y - vehicle.stopY) <= 12;

            if (nearStopLine) {
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
                this.visualVehicles.delete(id);
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
