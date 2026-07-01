# Migration Rollback Plan
**Prepared by:** ARB

## 1. Safety Procedures
- Before modifying any specification or module, the orchestrator caches the original file to `.aetheris/backup/`.
- Git checkpoints are tagged before and after each phase:
  - `pre-migration-checkpoint`
  - `phase-1-standardization`

## 2. Restore Steps
To revert changes:
1. `git reset --hard pre-migration-checkpoint`
2. Recover cached state from `.aetheris/backup/` if untracked files are modified.
