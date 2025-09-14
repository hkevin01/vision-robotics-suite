#!/bin/bash
# Test script to verify the complete Docker orchestration setup

set -e

echo "🔧 Vision Robotics Suite Docker Orchestration Test"
echo "================================================="

# Change to project directory
cd /home/kevin/Projects/vision-robotics-suite

# Make run.sh executable
chmod +x run.sh

echo "📋 Testing run.sh help command:"
./run.sh help

echo ""
echo "🔍 Testing GUI creation:"
./run.sh gui:create

echo ""
echo "📁 Verifying GUI files exist:"
ls -la gui/

echo ""
echo "🐳 Testing Docker build:"
./run.sh build

echo ""
echo "✅ All tests passed! Ready to run: ./run.sh up"
