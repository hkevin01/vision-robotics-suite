#!/bin/bash

echo "🧹 Moving Python files to tools/git-scripts/"

# Move git-related Python files
mv commit_all.py tools/git-scripts/
mv commit_now.py tools/git-scripts/
mv commit_strategy.py tools/git-scripts/
mv execute_commit.py tools/git-scripts/
mv execute_final.py tools/git-scripts/
mv execute_universal_commit.py tools/git-scripts/
mv final_cleanup.py tools/git-scripts/
mv final_stage_commit.py tools/git-scripts/
mv final_universal_commit.py tools/git-scripts/
mv git_commit_clean.py tools/git-scripts/
mv quick_commit.py tools/git-scripts/
mv run_complete_final.py tools/git-scripts/
mv run_final_git.py tools/git-scripts/
mv run_universal.py tools/git-scripts/
mv simple_commit.py tools/git-scripts/
mv simple_git.py tools/git-scripts/
mv universal_commit.py tools/git-scripts/
mv universal_final_commit.py tools/git-scripts/

echo "🧹 Moving demo Python files to tools/demo-scripts/"

# Move demo Python files
mv demo_advanced_features.py tools/demo-scripts/
mv demo_final.py tools/demo-scripts/
mv simple_demo.py tools/demo-scripts/
mv simple_execute.py tools/demo-scripts/
mv simple_final.py tools/demo-scripts/

echo "🧹 Moving shell scripts to tools/shell-scripts/"

# Move shell scripts (except run.sh)
mv commit_clean_files.sh tools/shell-scripts/
mv complete_final.sh tools/shell-scripts/
mv final_commit.sh tools/shell-scripts/
mv final_git_commit.sh tools/shell-scripts/
mv fix_git_status.sh tools/shell-scripts/
mv make_executable.sh tools/shell-scripts/
mv run_commit.sh tools/shell-scripts/
mv run_execute_commit.sh tools/shell-scripts/
mv run_final_commit.sh tools/shell-scripts/
mv stage_and_commit.sh tools/shell-scripts/
mv stage_clean_files.sh tools/shell-scripts/
mv test_setup.sh tools/shell-scripts/
mv universal_final.sh tools/shell-scripts/

echo "🧹 Moving Markdown files to docs/project-status/"

# Move markdown files (except README.md)
mv COMPLETION_SUMMARY.md docs/project-status/
mv DOCKER_ORCHESTRATION.md docs/project-status/
mv DOCKER_STRATEGY.md docs/project-status/
mv GIT_STATUS_RESOLUTION.md docs/project-status/
mv PROJECT_SUMMARY.md docs/project-status/
mv STAGING_STATUS.md docs/project-status/

echo "✅ File organization complete!"
