CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    file_hash VARCHAR(64) DEFAULT NULL,
    file_data BYTEA NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_size BIGINT NOT NULL,
    transaction_id VARCHAR(64) DEFAULT NULL
);

CREATE INDEX idx_file_hash ON files(file_hash); 