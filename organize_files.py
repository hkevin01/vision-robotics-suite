#!/usr/bin/env python3
"""
Organize files in the Vision Robotics Suite root directory
Move Python scripts, shell scripts, and markdown files to appropriate subfolders
"""
import os
import shutil

def move_files():
    root_dir = "/home/kevin/Projects/vision-robotics-suite"

    # Define file mappings
    git_scripts = [
        "commit_all.py", "commit_now.py", "commit_strategy.py", "execute_commit.py",
        "execute_final.py", "execute_universal_commit.py", "final_cleanup.py",
        "final_stage_commit.py", "final_universal_commit.py", "git_commit_clean.py",
        "quick_commit.py", "run_complete_final.py", "run_final_git.py",
        "run_universal.py", "simple_commit.py", "simple_execute.py",
        "simple_final.py", "simple_git.py", "universal_commit.py",
        "universal_final_commit.py"
    ]

    demo_scripts = [
        "demo_advanced_features.py", "demo_final.py", "simple_demo.py"
    ]

    shell_scripts = [
        "commit_clean_files.sh", "complete_final.sh", "final_commit.sh",
        "final_git_commit.sh", "fix_git_status.sh", "make_executable.sh",
        "run_commit.sh", "run_execute_commit.sh", "run_final_commit.sh",
        "stage_and_commit.sh", "stage_clean_files.sh", "test_setup.sh",
        "universal_final.sh"
    ]

    project_docs = [
        "COMPLETION_SUMMARY.md", "DOCKER_ORCHESTRATION.md", "DOCKER_STRATEGY.md",
        "GIT_STATUS_RESOLUTION.md", "PROJECT_SUMMARY.md", "STAGING_STATUS.md"
    ]

    # Move git scripts
    print("🔧 Moving Git automation scripts...")
    for script in git_scripts:
        src = os.path.join(root_dir, script)
        dst = os.path.join(root_dir, "tools", "git-scripts", script)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✅ Moved {script}")
        else:
            print(f"  ⚠️  {script} not found")

    # Move demo scripts
    print("\n🎮 Moving Demo scripts...")
    for script in demo_scripts:
        src = os.path.join(root_dir, script)
        dst = os.path.join(root_dir, "tools", "demo-scripts", script)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✅ Moved {script}")
        else:
            print(f"  ⚠️  {script} not found")

    # Move shell scripts
    print("\n🐚 Moving Shell scripts...")
    for script in shell_scripts:
        src = os.path.join(root_dir, script)
        dst = os.path.join(root_dir, "tools", "shell-scripts", script)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✅ Moved {script}")
        else:
            print(f"  ⚠️  {script} not found")

    # Move project documentation
    print("\n📚 Moving Project documentation...")
    for doc in project_docs:
        src = os.path.join(root_dir, doc)
        dst = os.path.join(root_dir, "docs", "project-status", doc)
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✅ Moved {doc}")
        else:
            print(f"  ⚠️  {doc} not found")

    print("\n🎉 File organization complete!")
    print("\n📋 Root directory should now be clean except for:")
    print("  - README.md (project documentation)")
    print("  - run.sh (main execution script)")
    print("  - pyproject.toml, poetry.lock (package management)")
    print("  - Makefile, docker-compose files (build configuration)")
    print("  - Dockerfile (container configuration)")

if __name__ == "__main__":
    move_files()
