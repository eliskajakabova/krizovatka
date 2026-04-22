export class WebSocketClient {
    constructor(onSetup, onState, onCompleted) {
        this.ws = null;
        this.onSetup = onSetup;
        this.onState = onState;
        this.onCompleted = onCompleted;
    }

    connect(simulationId, statusElement) {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        const wsUrl = `ws://127.0.0.1:8000/ws/${simulationId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            statusElement.textContent = 'Stav: WebSocket pripojený';
            statusElement.className = 'status connected';
        };

        this.ws.onclose = () => {
            statusElement.textContent = 'Stav: WebSocket odpojený';
            statusElement.className = 'status disconnected';
            this.ws = null;
        };

        this.ws.onerror = () => {
            statusElement.textContent = 'Stav: Chyba WebSocket spojenia';
            statusElement.className = 'status disconnected';
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'setup') {
                this.onSetup(data);
            } else if (data.type === 'state') {
                this.onState(data);
            } else if (data.type === 'completed') {
                this.onCompleted(data);
            } else if (data.type === 'error') {
                statusElement.textContent = `Stav: ${data.message}`;
                statusElement.className = 'status disconnected';
            }
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
