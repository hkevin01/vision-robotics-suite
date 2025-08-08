#!/usr/bin/env python3
import subprocess
import os

os.chdir("/home/kevin/Projects/vision-robotics-suite")

print("🔧 Complete final commit - staging ALL files...")

# Execute the bash script directly
result = subprocess.run(["bash", "complete_final.sh"], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Script executed successfully!")
    print(result.stdout)
else:
    print("❌ Script failed:")
    print(result.stderr)
    print(result.stdout)

# Also check final status
status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
remaining_files = status_result.stdout.strip()

if not remaining_files:
    print("🎉 REPOSITORY IS COMPLETELY CLEAN! All files committed.")
else:
    print(f"📋 {len(remaining_files.splitlines())} files still untracked:")
    for line in remaining_files.splitlines()[:10]:
        print(f"  {line}")

print("🚀 Ready for sync!")
