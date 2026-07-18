---
name: feature-workflow
description: "Use only when implementing a new product or code feature in a Git repository. Do not use for bug fixes, refactors, maintenance, documentation, configuration, or read-only tasks. Complete the feature autonomously in a worktree through verification, merge, push, and cleanup."
---

# Workflow

Always use a worktree for new features.

1. Inspect the repository and reuse or create a worktree without touching user changes.
2. Create an ignored `.agent-work/PROGRESS.md` and keep it current.
3. Create a feature branch using the repository's naming rules.
4. Implement the change only in the worktree.
5. Run the required baseline and final tests; fix failures.
6. Commit the intended changes and push the feature branch.
7. Merge into the default branch, test again, and push it without asking.
8. Delete the feature branch, progress file, and worktree after a successful push.

Complete the workflow autonomously. Never ask for merge approval, overwrite user
changes, or force destructive Git operations.
