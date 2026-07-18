---
name: feature-workflow
description: "Use for every task that changes a Git repository, including small code, documentation, and configuration edits. Complete the entire change autonomously in a worktree: implement, verify, commit, push, merge, push the default branch, and clean up. Skip only read-only tasks."
---

# Workflow

Always use a worktree — even for small changes.

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
