// js/api.js
const API_BASE = 'http://127.0.0.1:8000/api/v1/intersection';

export async function getConfigurations() {
    const response = await fetch(`${API_BASE}/configurations`);
    if (!response.ok) throw new Error('Chyba API');
    return await response.json();
}

// Pridali sme parametre duration a intensity
export async function startSimulation(configId, duration, intensity) {
    const payload = {
        config_id: configId,
        simulation_duration: duration,
        traffic_intensity: intensity
    };

    const response = await fetch(`${API_BASE}/simulations/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) throw new Error('Chyba pri štarte');
    return await response.json();
}

// Pridáme funkciu pre volanie STOP endpointu
export async function stopSimulation(simulationId) {
    const response = await fetch(`${API_BASE}/simulations/${simulationId}`, {
        method: 'DELETE'
    });
    if (!response.ok) throw new Error('Chyba pri zastavení');
    return await response.json();
}