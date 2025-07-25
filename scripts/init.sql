-- Initialize the database schema for Infinite Crew

-- Create the results table
CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY,
    parent_id UUID REFERENCES results(id),
    prompt TEXT NOT NULL,
    output TEXT,
    depth INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_results_parent_id ON results(parent_id);
CREATE INDEX IF NOT EXISTS idx_results_created_at ON results(created_at);
CREATE INDEX IF NOT EXISTS idx_results_depth ON results(depth);

-- Create a view for task statistics
CREATE OR REPLACE VIEW task_stats AS
SELECT 
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN output IS NOT NULL THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN output IS NULL THEN 1 END) as pending_tasks,
    AVG(depth) as avg_depth,
    MAX(depth) as max_depth
FROM results;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_results_updated_at BEFORE UPDATE ON results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();