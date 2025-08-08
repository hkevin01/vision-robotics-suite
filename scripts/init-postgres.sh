#!/bin/bash
# Database initialization script for PostgreSQL

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create additional databases for testing and analytics
    CREATE DATABASE vision_robotics_test;
    CREATE DATABASE vision_analytics;

    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE vision_robotics_test TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE vision_analytics TO $POSTGRES_USER;

    -- Create extensions
    \c vision_robotics
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    \c vision_robotics_test
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    \c vision_analytics
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Create initial schema for vision_robotics
    \c vision_robotics

    CREATE TABLE IF NOT EXISTS inspection_sessions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        status VARCHAR(50) DEFAULT 'active',
        configuration JSONB,
        metadata JSONB
    );

    CREATE TABLE IF NOT EXISTS defect_detections (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES inspection_sessions(id),
        defect_type VARCHAR(100) NOT NULL,
        position_x DECIMAL(10,3),
        position_y DECIMAL(10,3),
        size_width DECIMAL(10,3),
        size_height DECIMAL(10,3),
        severity DECIMAL(3,2),
        confidence DECIMAL(3,2),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB
    );

    CREATE TABLE IF NOT EXISTS point_cloud_registrations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES inspection_sessions(id),
        camera_id VARCHAR(100) NOT NULL,
        points_count INTEGER,
        registration_error DECIMAL(10,6),
        processing_time_ms INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        transformation_matrix JSONB,
        metadata JSONB
    );

    CREATE TABLE IF NOT EXISTS lighting_configurations (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID REFERENCES inspection_sessions(id),
        zone_id VARCHAR(100) NOT NULL,
        lighting_type VARCHAR(50),
        intensity INTEGER,
        color_temperature INTEGER,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB
    );

    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_inspection_sessions_created_at ON inspection_sessions(created_at);
    CREATE INDEX IF NOT EXISTS idx_defect_detections_session_id ON defect_detections(session_id);
    CREATE INDEX IF NOT EXISTS idx_defect_detections_type ON defect_detections(defect_type);
    CREATE INDEX IF NOT EXISTS idx_point_cloud_registrations_session_id ON point_cloud_registrations(session_id);
    CREATE INDEX IF NOT EXISTS idx_lighting_configurations_session_id ON lighting_configurations(session_id);

    -- Insert sample data for development
    INSERT INTO inspection_sessions (session_name, configuration, metadata) VALUES
    ('Demo Paint Inspection',
     '{"pixel_size_mm": 0.01, "min_defect_size_mm": 0.1}',
     '{"description": "Demonstration paint inspection session"}'),
    ('3D Registration Test',
     '{"cameras": 3, "accuracy_mm": 0.1}',
     '{"description": "Multi-camera 3D registration test"}'),
    ('Adaptive Lighting Demo',
     '{"zones": 5, "auto_adjust": true}',
     '{"description": "Adaptive lighting demonstration"}'
    );

EOSQL

echo "PostgreSQL database initialization completed successfully!"
