---
name: worktree-workflow
description: Run repository changes in an isolated Git worktree from preparation through verified delivery and cleanup. Use for every task that may modify files in a Git repository, including code, documentation, configuration, metadata, and small fixes. Skip only tasks that are guaranteed to remain read-only.
---

# Worktree Workflow

Keep the user's primary checkout untouched while making every repository change
in an isolated worktree. Preserve all existing work and stop whenever safe
completion requires user input.

## 1. Inspect before changing anything

1. Confirm that the target is a Git repository. If it is not, stop and ask
   whether to initialize one or work without this workflow.
2. Read the applicable repository instructions and identify setup, test, branch,
   and release conventions.
3. Inspect the current branch, status, remotes, remote default branch, and
   registered worktrees.
4. Preserve all pre-existing tracked, untracked, and ignored user files. Never
   stash, reset, overwrite, move, commit, or delete them.
5. Determine whether the current checkout is already a linked worktree by
   comparing the resolved Git directory with the resolved common Git directory.
   Treat a submodule as a normal checkout, not as a linked worktree.

If the task depends on uncommitted changes that are unavailable in the new
worktree, stop and ask how the user wants to handle them.

## 2. Enter an isolated worktree

- If already in a linked worktree, reuse it. Never create a nested worktree.
- Otherwise, prefer a native worktree or isolated-workspace facility supplied by
  the host application.
- If no native facility exists, create a manual worktree:
  1. Resolve the base branch from `origin/HEAD`. Fall back to an existing `main`
     or `master`; ask when the base remains ambiguous.
  2. Derive a short kebab-case task slug.
  3. Follow an applicable branch-prefix rule. If none exists, use
     `work/<task-slug>`.
  4. Add `.worktrees/` to the repository's local `.git/info/exclude` when it is
     not already ignored. Do not change the tracked `.gitignore` solely for the
     worktree.
  5. Create `.worktrees/<task-slug>` with a new branch based on the resolved base
     branch, then do all further work from that directory.

Do not continue in the primary checkout when worktree creation fails. Report the
failure and ask for direction.

## 3. Track temporary progress

1. Add `.agent-work/` to the local `.git/info/exclude` when needed.
2. Create `.agent-work/PROGRESS.md` inside the worktree.
3. Record the goal, implementation checklist, decisions, verification results,
   commit and push state, and the pending merge gate.
4. Update it throughout the task.

Never stage or commit `.agent-work/PROGRESS.md`. Preserve it while merge approval
is pending; remove it through successful worktree cleanup.

## 4. Establish a clean baseline

1. Run only the setup steps required by the repository and its manifests.
2. Run the repository's required tests before implementation.
3. If the baseline fails, record the failure, report it, and ask whether to
   investigate or continue. Do not silently attribute existing failures to the
   requested change.

## 5. Implement and verify

1. Implement the requested change only in the worktree.
2. Keep the progress file current as decisions and completed steps change.
3. Run tests and checks proportional to the change plus every mandatory command
   from repository instructions.
4. Inspect the final status and diff. Exclude unrelated changes and temporary
   files.
5. Do not claim completion unless the required verification passes. If a check
   cannot run, state why and treat verification as incomplete.

## 6. Commit and push the feature branch

1. Stage only intended files and create focused commit or commits.
2. Confirm that the temporary progress file and unrelated user files are absent
   from every commit.
3. Push the feature branch to its configured remote and establish upstream
   tracking.
4. If no suitable remote exists or the push fails, stop and report the exact
   state. Do not invent a remote, force-push, or skip the delivery failure.

## 7. Require merge approval

After verification, commit, and feature-branch push succeed, ask the user for
explicit permission to merge into the resolved default branch.

Until approval is given:

- Do not merge, push the default branch, delete either branch, or remove the
  worktree.
- Preserve `.agent-work/PROGRESS.md` so another session can resume safely.
- Report the feature branch, commit, remote, worktree path, and verification
  results.

Treat silence or an ambiguous response as no approval.

## 8. Merge and clean up after approval

1. Recheck every worktree and both branches. Require the primary checkout to be
   clean; if it is dirty, stop without changing it.
2. Fetch the remote and update the default branch with a fast-forward-only pull.
3. Merge the feature branch into the default branch without rewriting history.
   On conflict, stop and preserve the worktree and branch for recovery.
4. Run the required verification again on the merged result.
5. Push the default branch. Do not clean up if verification or this push fails.
6. After the default branch push succeeds, delete the remote feature branch,
   remove the temporary progress data and owned worktree, delete the local
   feature branch, and prune stale worktree metadata.
7. Use the host application's cleanup mechanism for a host-owned worktree; never
   manually remove an externally managed workspace.

If cleanup is only partially successful, report every remaining branch, path, or
remote ref. Never use forced deletion for unmerged or unverified work.

## Non-negotiable safeguards

- Never modify the primary checkout during implementation.
- Never bypass the baseline-failure or merge-approval gates.
- Never use destructive reset, forced checkout, forced push, or unapproved
  deletion to make the workflow succeed.
- Never report a merge, push, test, or cleanup as complete without verifying its
  actual result.
