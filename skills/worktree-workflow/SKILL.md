---
name: worktree-workflow
description: Use for every task that may change files in a Git repository, including small code, documentation, and configuration edits. Run the change in a worktree, track progress, verify it, commit and push it, then require approval before merging and cleaning up. Skip only read-only tasks.
---

# Workflow

Always use a worktree — even for small changes.

1. Inspect Git status and existing worktrees. Preserve all user changes. Reuse a
   linked worktree if already inside one; otherwise create one, preferring the
   host's native worktree support and falling back to `.worktrees/<task-slug>`.
2. Create an ignored `.agent-work/PROGRESS.md` and keep the task checklist,
   decisions, and test results current. Never commit it.
3. Create or confirm a feature branch, following repository or agent naming
   rules; use `work/<task-slug>` when no rule exists.
4. Implement the requested change only in the worktree.
5. Verify with the repository's required tests. If the baseline or final tests
   fail, stop, report the failure, and ask what to do.
6. Commit only the intended changes and push the feature branch.
7. Ask for explicit approval before merging. Until approval, keep the branch,
   progress file, and worktree intact.
8. After approval, require a clean primary checkout, update the default branch,
   merge, verify again, and push. Only then delete the remote and local feature
   branches, progress file, and owned worktree.

Stop instead of forcing when worktree creation, the remote, tests, merge, or
cleanup fails. Never stash, reset, overwrite, force-push, or delete user work.
