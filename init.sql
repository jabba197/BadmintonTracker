-- init.sql
-- SQL script to create the matches table

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY, -- Auto-incrementing ID
    player1_name VARCHAR(100) NOT NULL,
    player2_name VARCHAR(100) NOT NULL,
    player1_score INTEGER NOT NULL,
    player2_score INTEGER NOT NULL,
    match_datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Automatically set timestamp
);

-- Optional: Add an index for faster lookups if needed
-- CREATE INDEX idx_match_datetime ON matches (match_datetime);
