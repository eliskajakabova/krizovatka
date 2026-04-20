export class WebSocketClient {
    constructor(onSetup, onState, onCompleted) {
        this.ws = null;
        this.onSetup = onSetup;
        this.onState = onState;
        this.onCompleted = onCompleted;
    }

    connect(simulationId, statusElement) {
        const wsUrl = `ws://127.0.0.1:8000/ws/${simulationId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            statusElement.textContent = "WebSocket: Pripojené";
            statusElement.className = "connected";
        };

        this.ws.onclose = () => {
            statusElement.textContent = "WebSocket: Odpojené";
            statusElement.className = "disconnected";
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === "setup") this.onSetup(data);
            else if (data.type === "state") this.onState(data);
            else if (data.type === "completed") this.onCompleted(data);
        };
    }

    disconnect() {
        if (this.ws) this.ws.close();
    }
}