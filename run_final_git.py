#!/usr/bin/env python3
import os
import subprocess

os.chdir("/home/kevin/Projects/vision-robotics-suite")

# Make script executable
subprocess.call(["chmod", "+x", "final_git_commit.sh"])

# Execute the final commit
subprocess.call(["./final_git_commit.sh"])

print("🎉 Final commit process completed!")
