-- ============================================================================
-- 1. DIMENSION TABLES
-- ============================================================================

CREATE TABLE dim_sensors (
    sensor_id SERIAL PRIMARY KEY,
    topic VARCHAR(255) UNIQUE,
    location VARCHAR(100),
    measurement_type VARCHAR(50)
);

-- ============================================================================
-- 2. FACT TABLES
-- ============================================================================

CREATE TABLE fact_measurements (
    measurement_id BIGSERIAL PRIMARY KEY,
    sensor_id INT REFERENCES dim_sensors(sensor_id),
    value NUMERIC(10, 2),
    timestamp TIMESTAMP
);

CREATE TABLE fact_incidents (
    incident_id SERIAL PRIMARY KEY,
    sensor_id INT REFERENCES dim_sensors(sensor_id),
    value_at_incident NUMERIC(10, 2),
    previous_value NUMERIC(10, 2),
    timestamp TIMESTAMP,
    incident_type VARCHAR(50)
);

-- ============================================================================
-- 2b. CONFIG TABLES
-- ============================================================================

CREATE TABLE config_thresholds (
    threshold_id SERIAL PRIMARY KEY,
    measurement_type VARCHAR(50) UNIQUE,
    threshold_value NUMERIC(10, 2),
    description VARCHAR(255)
);

INSERT INTO config_thresholds (measurement_type, threshold_value, description) VALUES
    ('temperature', 5.0, 'Max allowed temperature deviation'),
    ('humidity', 10.0, 'Max allowed humidity deviation');

-- ============================================================================
-- 3. ANALYTICS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW view_sensor_analytics AS
SELECT
    m.timestamp,
    s.location,
    s.measurement_type,
    m.value,
    AVG(m.value) OVER (
        PARTITION BY m.sensor_id
        ORDER BY m.timestamp
        RANGE BETWEEN INTERVAL '10 minutes' PRECEDING AND CURRENT ROW
    ) AS voortschrijdend_gemiddelde_10min,
    AVG(m.value) OVER (
        PARTITION BY m.sensor_id, (m.timestamp::DATE)
    ) AS daggemiddelde,
    CASE WHEN fi.incident_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_incident
FROM fact_measurements m
JOIN dim_sensors s ON m.sensor_id = s.sensor_id
LEFT JOIN fact_incidents fi
    ON m.sensor_id = fi.sensor_id
    AND m.timestamp = fi.timestamp;
