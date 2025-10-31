-- Drop the table if it already exists (optional)
DROP TABLE IF EXISTS conversations;

-- Create the conversations table
CREATE TABLE conversations (
    conversation_id SERIAL PRIMARY KEY,
    status_id INT NOT NULL,

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,

    -- Foreign key constraints
    CONSTRAINT fk_status
        FOREIGN KEY (status_id)
        REFERENCES status (status_id)
        ON DELETE SET NULL
);

-- ✅ Optional: Indexes for performance
CREATE INDEX idx_conversations_status_id ON conversations(status_id);