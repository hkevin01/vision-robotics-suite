#!/bin/bash
# Stage the clean files (no lint errors)
echo "Staging clean robotics and vision system files..."

git add src/robot_programming/multi_robot_collision_avoidance.py
git add src/robot_programming/universal_robots/collaborative_safety_zones.py
git add src/vision_systems/battery_pack_quality_control.py
git add src/vision_systems/body_in_white_inspection.py
git add src/vision_systems/engine_timing_chain_verification.py

echo "Clean files staged successfully!"
git status --porcelain
