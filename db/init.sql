CREATE TABLE IF NOT EXISTS predictions_log (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    tenure FLOAT,
    monthly_charges FLOAT,
    total_charges FLOAT,
    senior_citizen INT,
    input_payload JSONB,
    prediction VARCHAR(10),
    latency_ms FLOAT
);
