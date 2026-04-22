import { getConfigurations, startSimulation, stopSimulation } from './api.js';
import { WebSocketClient } from './websocket.js';
import { IntersectionRenderer } from './canvas.js';

// HTML Elementy - Ovládanie
const configSelect = document.getElementById('configSelect');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const resetBtn = document.getElementById('resetBtn');
const statusBox = document.getElementById('statusBox');

// HTML Elementy - Parametre
const inputDur = document.getElementById('simDuration');
const inN = document.getElementById('intNorth');
const inS = document.getElementById('intSouth');
const inE = document.getElementById('intEast');
const inW = document.getElementById('intWest');

// HTML Elementy - Štatistiky
const statTime = document.getElementById('statTime');
const statGen = document.getElementById('statGenerated');
const statPass = document.getElementById('statPassed');
const statWait = document.getElementById('statWaiting');
const statQueue = document.getElementById('statQueue');

let currentSimulationId = null;

// Inicializácia kreslenia
const renderer = new IntersectionRenderer('simCanvas');
renderer.drawStaticBackground();

function setStatus(message, isConnected = false) {
    statusBox.textContent = message;
    statusBox.className = isConnected
        ? 'status connected'
        : 'status disconnected';
}

function resetStats() {
    statTime.textContent = '0.0';
    statGen.textContent = '0';
    statPass.textContent = '0';
    statWait.textContent = '0';
    statQueue.textContent = '0, 0, 0, 0';
}

function enableUI(isRunning) {
    startBtn.disabled = isRunning;
    stopBtn.disabled = !isRunning;
    resetBtn.disabled = isRunning;
    configSelect.disabled = isRunning;
    inputDur.disabled = isRunning;
    inN.disabled = isRunning;
    inS.disabled = isRunning;
    inE.disabled = isRunning;
    inW.disabled = isRunning;
}

// Callbacks pre WebSocket
const onSetup = (data) => {
    console.log('Setup prijatý:', data);
    setStatus(`Stav: Pripojené (${data.simulation_id})`, true);
};

const onState = (data) => {
    statTime.textContent = Number(data.time).toFixed(1);
    statGen.textContent = data.statistics.total_vehicles_generated;
    statPass.textContent = data.statistics.total_vehicles_passed;
    statWait.textContent = data.statistics.total_vehicles_waiting;
    statQueue.textContent = `${data.queue_lengths.north}, ${data.queue_lengths.south}, ${data.queue_lengths.east}, ${data.queue_lengths.west}`;

    renderer.renderFrame(data);
};

const onCompleted = (data) => {
    console.log('Simulácia dokončená:', data);
    alert('Simulácia skončila!');

    wsClient.disconnect();
    currentSimulationId = null;
    enableUI(false);
    setStatus('Stav: Simulácia dokončená', false);
};

const wsClient = new WebSocketClient(onSetup, onState, onCompleted);

// Po načítaní stránky stiahni konfigurácie z backendu
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await getConfigurations();

        configSelect.innerHTML = '';

        data.configurations.forEach((cfg) => {
            const opt = document.createElement('option');
            opt.value = cfg.config_id;
            opt.textContent = cfg.name;
            configSelect.appendChild(opt);
        });

        setStatus('Stav: Backend dostupný', false);
    } catch (e) {
        console.error('Chyba pri načítaní konfigurácií:', e);
        setStatus('Stav: Chyba spojenia s API', false);
    }
});

// Kliknutie na ŠTART
startBtn.addEventListener('click', async () => {
    renderer.clearVehicles();
    resetStats();

    const configId = configSelect.value;
    if (!configId) {
        alert('Vyberte konfiguráciu');
        return;
    }

    const duration = parseInt(inputDur.value, 10) || 60;
    const intensity = {
        north: parseInt(inN.value, 10) || 0,
        south: parseInt(inS.value, 10) || 0,
        east: parseInt(inE.value, 10) || 0,
        west: parseInt(inW.value, 10) || 0,
    };

    try {
        wsClient.disconnect();
        currentSimulationId = null;

        setStatus('Stav: Spúšťam simuláciu...', false);

        const data = await startSimulation(configId, duration, intensity);

        currentSimulationId = data.simulation_id;
        wsClient.connect(currentSimulationId, statusBox);
        enableUI(true);
    } catch (err) {
        console.error('Chyba pri spustení simulácie:', err);
        setStatus('Stav: Nepodarilo sa spustiť simuláciu', false);
        alert('Nepodarilo sa spustiť simuláciu.');
    }
});

// Kliknutie na STOP
stopBtn.addEventListener('click', async () => {
    if (!currentSimulationId) {
        return;
    }

    try {
        await stopSimulation(currentSimulationId);
        wsClient.disconnect();
        currentSimulationId = null;
        enableUI(false);
        setStatus('Stav: Simulácia zastavená', false);
    } catch (err) {
        console.error('Nepodarilo sa zastaviť simuláciu:', err);
        setStatus('Stav: Chyba pri zastavení simulácie', false);
    }
});

// Kliknutie na RESET
resetBtn.addEventListener('click', () => {
    wsClient.disconnect();
    currentSimulationId = null;

    renderer.clearVehicles();
    resetStats();
    renderer.drawStaticBackground();

    setStatus('Stav: Odpojené', false);
});
