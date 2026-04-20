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

// Callbacks pre WebSocket
const onSetup = (data) => console.log("Setup prijatý:", data);
const onState = (data) => {
    // 1. Aktualizuj UI štatistiky
    statTime.textContent = data.time.toFixed(1);
    statGen.textContent = data.statistics.total_vehicles_generated;
    statPass.textContent = data.statistics.total_vehicles_passed;
    statWait.textContent = data.statistics.total_vehicles_waiting;
    statQueue.textContent = `${data.queue_lengths.north}, ${data.queue_lengths.south}, ${data.queue_lengths.east}, ${data.queue_lengths.west}`;
    
    // 2. Kresli
    renderer.renderFrame(data);
};
const onCompleted = (data) => {
    alert("Simulácia skončila!");
    enableUI(false); // Vráti tlačidlá do stavu PRED spustením
};

const wsClient = new WebSocketClient(onSetup, onState, onCompleted);

// Po načítaní stránky stiahni konfigurácie z backendu
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const data = await getConfigurations();
        configSelect.innerHTML = '';
        data.configurations.forEach(cfg => {
            const opt = document.createElement('option');
            opt.value = cfg.config_id;
            opt.textContent = cfg.name;
            configSelect.appendChild(opt);
        });
    } catch (e) {
        statusBox.textContent = "Chyba spojenia s API";
        statusBox.className = "disconnected";
    }
});

function enableUI(isRunning) {
    startBtn.disabled = isRunning;
    stopBtn.disabled = !isRunning;
    resetBtn.disabled = isRunning; // Reset možný, len ak nebeží
    configSelect.disabled = isRunning;
    inputDur.disabled = isRunning;
    inN.disabled = isRunning; inS.disabled = isRunning;
    inE.disabled = isRunning; inW.disabled = isRunning;
}

// Kliknutie na ŠTART
startBtn.addEventListener('click', async () => {
    renderer.clearVehicles();
    const configId = configSelect.value;
    if (!configId) return alert("Vyberte konfiguráciu");

    const duration = parseInt(inputDur.value) || 60;
    const intensity = {
        north: parseInt(inN.value) || 0,
        south: parseInt(inS.value) || 0,
        east: parseInt(inE.value) || 0,
        west: parseInt(inW.value) || 0
    };

    try {
        wsClient.disconnect();
        const data = await startSimulation(configId, duration, intensity);
        currentSimulationId = data.simulation_id;
        wsClient.connect(currentSimulationId, statusBox);
        enableUI(true);
    } catch (err) {
        console.error("Chyba:", err);
    }
});

// Kliknutie na STOP
stopBtn.addEventListener('click', async () => {
    if (!currentSimulationId) return;
    try {
        await stopSimulation(currentSimulationId);
        wsClient.disconnect();
        enableUI(false);
    } catch (err) {
        console.error("Nepodarilo sa zastaviť:", err);
    }
});

// Kliknutie na RESET
resetBtn.addEventListener('click', () => {
    renderer.clearVehicles();
    
    // Vynulovanie štatistík
    statTime.textContent = "0.0";
    statGen.textContent = "0";
    statPass.textContent = "0";
    statWait.textContent = "0";
    statQueue.textContent = "0, 0, 0, 0";
    
    // Prekreslenie čistej križovatky
    renderer.drawStaticBackground();
});