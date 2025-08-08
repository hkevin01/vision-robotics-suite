// MongoDB initialization script

// Switch to vision_robotics database
db = db.getSiblingDB('vision_robotics');

// Create collections with initial data
db.createCollection('inspection_sessions');
db.createCollection('defect_detections');
db.createCollection('point_cloud_registrations');
db.createCollection('lighting_configurations');

// Insert sample inspection sessions
db.inspection_sessions.insertMany([
    {
        _id: ObjectId(),
        session_name: "Demo Paint Inspection",
        created_at: new Date(),
        updated_at: new Date(),
        status: "active",
        configuration: {
            pixel_size_mm: 0.01,
            min_defect_size_mm: 0.1,
            scratch_sensitivity: 0.8,
            crater_sensitivity: 0.7
        },
        metadata: {
            description: "Demonstration paint inspection session",
            inspector: "system",
            part_type: "automotive_panel"
        }
    },
    {
        _id: ObjectId(),
        session_name: "3D Registration Test",
        created_at: new Date(),
        updated_at: new Date(),
        status: "active",
        configuration: {
            cameras: 3,
            accuracy_mm: 0.1,
            registration_method: "icp_with_ransac"
        },
        metadata: {
            description: "Multi-camera 3D registration test",
            workspace_bounds: [[-300, -300, 0], [300, 300, 200]]
        }
    },
    {
        _id: ObjectId(),
        session_name: "Adaptive Lighting Demo",
        created_at: new Date(),
        updated_at: new Date(),
        status: "active",
        configuration: {
            zones: 5,
            auto_adjust: true,
            quality_targets: {
                min_brightness: 50,
                max_brightness: 200,
                min_contrast: 30
            }
        },
        metadata: {
            description: "Adaptive lighting demonstration",
            lighting_types: ["LED_RING", "LED_BAR", "LED_DOME"]
        }
    }
]);

// Insert sample defect detections
db.defect_detections.insertMany([
    {
        _id: ObjectId(),
        session_name: "Demo Paint Inspection",
        defect_type: "SCRATCH",
        position: {x: 150.5, y: 200.3},
        size: {width: 0.8, height: 45.2},
        severity: 0.7,
        confidence: 0.95,
        created_at: new Date(),
        metadata: {
            detection_algorithm: "halcon_scratch_detection",
            image_quality: "high"
        }
    },
    {
        _id: ObjectId(),
        session_name: "Demo Paint Inspection",
        defect_type: "CRATER",
        position: {x: 300.1, y: 150.7},
        size: {width: 2.1, height: 2.3},
        severity: 0.4,
        confidence: 0.88,
        created_at: new Date(),
        metadata: {
            detection_algorithm: "halcon_crater_detection",
            depth_mm: 0.03
        }
    }
]);

// Insert sample point cloud registrations
db.point_cloud_registrations.insertMany([
    {
        _id: ObjectId(),
        session_name: "3D Registration Test",
        camera_id: "phoxi_01",
        points_count: 50247,
        registration_error: 0.0034,
        processing_time_ms: 245,
        created_at: new Date(),
        transformation_matrix: [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ],
        metadata: {
            algorithm: "icp",
            iterations: 15,
            convergence: true
        }
    },
    {
        _id: ObjectId(),
        session_name: "3D Registration Test",
        camera_id: "phoxi_02",
        points_count: 48123,
        registration_error: 0.0041,
        processing_time_ms: 289,
        created_at: new Date(),
        transformation_matrix: [
            [0.966, -0.259, 0.0, 200.0],
            [0.259, 0.966, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ],
        metadata: {
            algorithm: "icp",
            iterations: 18,
            convergence: true
        }
    }
]);

// Insert sample lighting configurations
db.lighting_configurations.insertMany([
    {
        _id: ObjectId(),
        session_name: "Adaptive Lighting Demo",
        zone_id: "ring_led_main",
        lighting_type: "LED_RING",
        intensity: 2048,
        color_temperature: 6500,
        is_active: true,
        created_at: new Date(),
        metadata: {
            position: [0, 0, 100],
            angle: [0, 45],
            max_intensity: 4095
        }
    },
    {
        _id: ObjectId(),
        session_name: "Adaptive Lighting Demo",
        zone_id: "bar_led_side_01",
        lighting_type: "LED_BAR",
        intensity: 1536,
        color_temperature: 5000,
        is_active: true,
        created_at: new Date(),
        metadata: {
            position: [100, 0, 80],
            angle: [30, 30],
            max_intensity: 4095
        }
    }
]);

// Create indexes for performance
db.inspection_sessions.createIndex({created_at: -1});
db.inspection_sessions.createIndex({status: 1});
db.defect_detections.createIndex({session_name: 1});
db.defect_detections.createIndex({defect_type: 1});
db.defect_detections.createIndex({created_at: -1});
db.point_cloud_registrations.createIndex({session_name: 1});
db.point_cloud_registrations.createIndex({camera_id: 1});
db.lighting_configurations.createIndex({session_name: 1});
db.lighting_configurations.createIndex({zone_id: 1});

print("MongoDB initialization completed successfully!");
print("Created collections: inspection_sessions, defect_detections, point_cloud_registrations, lighting_configurations");
print("Inserted sample data for development and testing");
