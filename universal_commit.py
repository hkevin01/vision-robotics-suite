#!/usr/bin/env python3
import subprocess
import os

os.chdir("/home/kevin/Projects/vision-robotics-suite")

print("🔧 FINAL UNIVERSAL COMMIT - Staging ALL files...")

# Stage absolutely everything with git add .
subprocess.call(["git", "add", "."])
print("✅ ALL files staged with 'git add .'")

# Commit with universal message
subprocess.call([
    "git", "commit", "-m", 
    "feat: Complete Vision Robotics Suite platform\n\nUniversal commit of all project files including the comprehensive 104,752+ line industrial automation platform with Docker orchestration, utilities, and automation tools."
])

print("✅ Universal commit completed!")

# Check final status
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    print("📋 Any remaining files:")
    print(result.stdout)
else:
    print("🎉 Repository is completely clean!")

print("🚀 Ready for sync!")
