#!/usr/bin/env python3
import subprocess
import os

os.chdir("/home/kevin/Projects/vision-robotics-suite")

# Make the script executable
subprocess.call(["chmod", "+x", "universal_final.sh"])

# Execute it
subprocess.call(["./universal_final.sh"])
