# Error Recovery

Expect the workflow to fail in normal ways. Optimize for quick diagnosis, honest recovery, and minimal queue/tracker corruption.

## 1. Wrong GitHub identity

Symptoms:
- `gh whoami` shows the wrong account
- push goes to the wrong fork
- HTTPS push uses cached credentials from another workspace

Recovery:
1. stop before pushing more commits
2. run `gh whoami`
3. check `git remote -v`
4. prefer an SSH fork remote tied to the intended account
5. confirm repo-local `git config user.name` and `git config user.email`
6. only then retry the push

## 2. Push rejected

Common causes:
- fork branch moved
- remote branch already exists with different history
- upstream changes require rebase

Recovery:
1. fetch both upstream and fork
2. inspect whether the branch is safe to rebase
3. rebase or reset only if you understand the branch state
4. rerun the narrow validation you previously claimed
5. push again

If the branch history is messy or ambiguous, stop and inspect before force-pushing.

## 3. PR template or policy bot failure

Symptoms:
- bot says PR body is malformed
- template sections missing
- issue-linking format rejected

Recovery:
1. read the exact repo template
2. repair the PR body to match the template literally
3. keep validation notes honest
4. do not argue with the bot if the format is satisfiable

## 4. CLA or DCO blocker

Treat this as actionable when you can honestly satisfy it.

Recovery:
1. read the bot comment carefully
2. follow the documented signing flow or signed-off-commit flow
3. if a new commit is required, amend or create the minimal corrective commit
4. rerun any validation invalidated by that commit

If the gate requires manual access you do not have, stop and document that clearly.

## 5. CI failure

Split failures into two buckets.

Usually actionable:
- lint/test/typecheck failures tied to touched code
- template or compliance failures you can repair
- requested review changes encoded as checks

Usually not actionable:
- third-party preview authorization gates
- unrelated flaky infra
- failures needing admin-only reruns or secrets you do not control

Recovery:
1. inspect the failing job log
2. decide whether it is patch-related or ambient noise
3. fix only the actionable failures
4. keep notes honest in the PR or tracker

## 6. Merge conflict or stale branch

Recovery:
1. fetch latest upstream
2. inspect the conflicting files before rebasing blindly
3. preserve the narrow scope of the original fix
4. rerun validation on the rebased branch

If rebasing reveals the issue is already fixed upstream, close or defer the work.

## 7. Duplicate issue or already-open PR discovered late

Recovery:
1. stop new work immediately
2. mark the queue item `blocked` or `closed` with the exact duplicate reason
3. if you already opened a redundant PR, close it politely unless maintainers want it kept
4. update tracker notes so the system does not rediscover it next run

## 8. Stale bot closed the PR

Recovery:
1. decide whether the fix is still worth pursuing
2. check whether new upstream changes superseded it
3. if still valuable and repo norms allow it, reopen or open a fresh PR with updated context
4. otherwise mark it `closed` or `deferred`

## 9. Rate limit hit

Recovery:
1. inspect remaining GitHub quota
2. back off instead of hammering retries
3. batch reads where safe
4. prefer tracker sync over new issue discovery when quota is low

## 10. Queue or tracker corruption

Symptoms:
- malformed JSON
- duplicate claims
- impossible status combinations
- tracker says merged while queue still says queued

Recovery:
1. stop automation that mutates the files
2. run the validation helper
3. fix the smallest broken records first
4. prefer explicit notes over silent repair when the history is ambiguous
5. resume automation only after validation passes

## Recovery philosophy

- preserve truth over momentum
- prefer small repairs over large rewrites
- document why an item was blocked or closed
- never fake validation just to clear a blocker
- if you are uncertain whether a recovery step is safe, stop and inspect
