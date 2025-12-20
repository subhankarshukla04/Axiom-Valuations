-- Migration Script: Scenario and Macro Assumptions Schema

-- Table for storing scenarios
CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('Bear', 'Base', 'Bull')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing macro assumptions
CREATE TABLE macro_assumptions (
    id SERIAL PRIMARY KEY,
    scenario_id INT REFERENCES scenarios(id) ON DELETE CASCADE,
    assumption_key VARCHAR(255) NOT NULL,
    assumption_value NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_scenarios_type ON scenarios(type);
CREATE INDEX idx_macro_assumptions_scenario_id ON macro_assumptions(scenario_id);