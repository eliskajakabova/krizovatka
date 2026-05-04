CREATE TABLE IF NOT EXISTS configurations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    cycle_duration INTEGER NOT NULL,
    signal_timings JSON NOT NULL,
    is_preset BOOLEAN DEFAULT FALSE,
    cycle_utilization FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulations (
    id VARCHAR(50) PRIMARY KEY,
    config_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    simulation_duration INTEGER,
    traffic_intensity JSON,
    vehicle_speed FLOAT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_vehicles_generated INTEGER,
    total_vehicles_passed INTEGER,
    average_wait_time FLOAT,
    max_wait_time FLOAT,
    intersection_utilization FLOAT,
    FOREIGN KEY (config_id) REFERENCES configurations(id)
);


INSERT INTO configurations (id, name, description, cycle_duration, signal_timings, is_preset)
VALUES (
    'cfg_preset01',
    'Základná konfigurácia',
    'Prednastavená konfigurácia pre štandardnú križovatku',
    136,
    '{
        "N_S": {"start": 0,   "duration": 45},
        "N_R": {"start": 0,   "duration": 45},
        "N_L": {"start": 45,  "duration": 10},
        "S_S": {"start": 0,   "duration": 45},
        "S_R": {"start": 0,   "duration": 45},
        "S_L": {"start": 56,  "duration": 10},
        "E_S": {"start": 70,  "duration": 45},
        "E_R": {"start": 70,  "duration": 45},
        "E_L": {"start": 115, "duration": 10},
        "W_S": {"start": 70,  "duration": 45},
        "W_R": {"start": 70,  "duration": 45},
        "W_L": {"start": 126, "duration": 10}
    }',
    TRUE
) ON CONFLICT (id) DO NOTHING;


INSERT INTO configurations (id, name, description, cycle_duration, signal_timings, is_preset)
VALUES (
    'cfg_preset02',
    'Rýchle striedanie',
    'Krátky cyklus s rýchlym striedaním smerov',
    60,
    '{
        "N_S": {"start": 0,  "duration": 10},
        "N_R": {"start": 0,  "duration": 10},
        "N_L": {"start": 10, "duration": 10},
        "S_S": {"start": 0,  "duration": 10},
        "S_R": {"start": 0,  "duration": 10},
        "S_L": {"start": 20, "duration": 10},
        "E_S": {"start": 30, "duration": 10},
        "E_R": {"start": 30, "duration": 10},
        "E_L": {"start": 40, "duration": 10},
        "W_S": {"start": 30, "duration": 10},
        "W_R": {"start": 30, "duration": 10},
        "W_L": {"start": 50, "duration": 10}
    }',
    TRUE
) ON CONFLICT (id) DO NOTHING;