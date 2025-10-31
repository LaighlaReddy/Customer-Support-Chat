-- Drop the table if it already exists (optional)
DROP TABLE IF EXISTS role;

-- Create the status table
CREATE TABLE role (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,

    -- Optional: add timestamps for tracking creation/updates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to auto-update `updated_at` when record is modified
CREATE OR REPLACE FUNCTION update_role_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_role_timestamp
BEFORE UPDATE ON role
FOR EACH ROW
EXECUTE FUNCTION update_role_timestamp();