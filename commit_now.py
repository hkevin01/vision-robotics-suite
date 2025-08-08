#!/usr/bin/env python3
import subprocess
import os

os.chdir("/home/kevin/Projects/vision-robotics-suite")

print("🔧 Executing universal commit NOW...")

# Stage everything
subprocess.call(["git", "add", "."])
print("✅ All files staged")

# Commit 
subprocess.call(["git", "commit", "-m", "feat: Universal commit - Complete Vision Robotics Suite platform with all utilities"])
print("✅ Committed!")

# Check final status
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=False)
if result.stdout.strip():
    print("Remaining:")
    print(result.stdout)
else:
    print("🎉 CLEAN!")

print("🚀 Done!")
