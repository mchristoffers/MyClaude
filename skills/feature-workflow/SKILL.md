---
name: feature-workflow
description: "Use only when implementing a new product or code feature in a Git repository. Do not use for bug fixes, refactors, maintenance, documentation, configuration, or read-only tasks. Complete the feature autonomously in a worktree through verification, merge, push, and cleanup."
---

# Workflow

Always use a worktree for new features.

- Commit every existing change to the default branch with a suitable message and push before starting.
- Inspect the repository and reuse or create a worktree.
- Create an ignored `.agent-work/PROGRESS.md` and keep it current.
- Create a feature branch using the repository's naming rules.
- Plan the implementation natively with the host's GPT-5.6 Sol (`gpt-5.6-sol`), never through OpenRouter.
- Implement the plan only in the worktree with Kimi K2.7 Code
  (`moonshotai/kimi-k2.7-code`) through OpenRouter.
- Run the required baseline and final tests; fix failures.
- Commit the intended changes and push the feature branch.
- Merge into the default branch and push it without asking.
- Delete the feature branch, progress file, and worktree after a successful push.

Complete the workflow autonomously. Never ask for merge approval, overwrite user
changes, or force destructive Git operations.
