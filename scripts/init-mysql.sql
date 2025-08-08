-- MySQL database initialization script
-- Create additional databases
CREATE DATABASE IF NOT EXISTS vision_robotics_test;
CREATE DATABASE IF NOT EXISTS vision_analytics;
-- Switch to main database
USE vision_robotics;
-- Create inspection_sessions table
CREATE TABLE IF NOT EXISTS inspection_sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    session_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    configuration JSON,
    metadata JSON
);
-- Create defect_detections table
CREATE TABLE IF NOT EXISTS defect_detections (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    session_id VARCHAR(36),
    defect_type VARCHAR(100) NOT NULL,
    position_x DECIMAL(10, 3),
    position_y DECIMAL(10, 3),
    size_width DECIMAL(10, 3),
    size_height DECIMAL(10, 3),
    severity DECIMAL(3, 2),
    confidence DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES inspection_sessions(id)
);
-- Create point_cloud_registrations table
CREATE TABLE IF NOT EXISTS point_cloud_registrations (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    session_id VARCHAR(36),
    camera_id VARCHAR(100) NOT NULL,
    points_count INTEGER,
    registration_error DECIMAL(10, 6),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transformation_matrix JSON,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES inspection_sessions(id)
);
-- Create lighting_configurations table
CREATE TABLE IF NOT EXISTS lighting_configurations (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    session_id VARCHAR(36),
    zone_id VARCHAR(100) NOT NULL,
    lighting_type VARCHAR(50),
    intensity INTEGER,
    color_temperature INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES inspection_sessions(id)
);
-- Create indexes for performance
CREATE INDEX idx_inspection_sessions_created_at ON inspection_sessions(created_at);
CREATE INDEX idx_defect_detections_session_id ON defect_detections(session_id);
CREATE INDEX idx_defect_detections_type ON defect_detections(defect_type);
CREATE INDEX idx_point_cloud_registrations_session_id ON point_cloud_registrations(session_id);
CREATE INDEX idx_lighting_configurations_session_id ON lighting_configurations(session_id);
-- Insert sample data for development
INSERT INTO inspection_sessions (session_name, configuration, metadata)
VALUES (
        'Demo Paint Inspection',
        '{"pixel_size_mm": 0.01, "min_defect_size_mm": 0.1}',
        '{"description": "Demonstration paint inspection session"}'
    ),
    (
        '3D Registration Test',
        '{"cameras": 3, "accuracy_mm": 0.1}',
        '{"description": "Multi-camera 3D registration test"}'
    ),
    (
        'Adaptive Lighting Demo',
        '{"zones": 5, "auto_adjust": true}',
        '{"description": "Adaptive lighting demonstration"}'
    );
