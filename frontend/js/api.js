const API_BASE = 'http://127.0.0.1:8000/api/intersection';

async function parseResponse(response, defaultMessage) {
    if (response.ok) {
        return await response.json();
    }

    let errorMessage = defaultMessage;

    try {
        const errorData = await response.json();

        if (errorData?.detail?.message) {
            errorMessage = errorData.detail.message;
        } else if (errorData?.detail && typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        }
    } catch {
        // ak response nie je JSON, necháme default message
    }

    throw new Error(errorMessage);
}

export async function getConfigurations() {
    const response = await fetch(`${API_BASE}/configurations`);
    return await parseResponse(response, 'Nepodarilo sa načítať konfigurácie.');
}

export async function startSimulation(configId, duration, intensity) {
    const payload = {
        config_id: configId,
        simulation_duration: duration,
        traffic_intensity: intensity,
    };

    const response = await fetch(`${API_BASE}/simulations/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });

    return await parseResponse(response, 'Nepodarilo sa spustiť simuláciu.');
}

export async function stopSimulation(simulationId) {
    const response = await fetch(`${API_BASE}/simulations/${simulationId}`, {
        method: 'DELETE',
    });

    return await parseResponse(response, 'Nepodarilo sa zastaviť simuláciu.');
}
