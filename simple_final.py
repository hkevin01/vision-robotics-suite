#!/usr/bin/env python3
import subprocess
import os

os.chdir("/home/kevin/Projects/vision-robotics-suite")
subprocess.call(["git", "add", "."])
subprocess.call(["git", "commit", "-m", "feat: Complete platform"])
subprocess.call(["git", "status", "--porcelain"])
print("DONE")
