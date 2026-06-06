# Automated Release Architecture Context

## Context Overview
This project completely bypasses automated version calculation engines (like traditional `semantic-release`) to prevent version conflicts caused by concurrent Pull Requests. Instead, it relies on a **Changelog-Driven Release** strategy.

## Why Must Every Modification Create a New Version?
In this repository, the `CHANGELOG.md` file is treated as the **Single Source of Truth (SSOT)** for the system's state. 

1. **Gatekeeping via PR:** When a developer opens a Pull Request, the validation workflow checks if `CHANGELOG.md` was altered against `main`. If no changes are found, the PR cannot be merged.
2. **Predictable Concurrency:** If multiple PRs are open simultaneously, they will catch version collisions (e.g., two devs trying to use `v1.1.0`) right during the PR stage, because the pipeline validates uniqueness against the GitHub API before letting the code in.
3. **Automated Metadata Extraction:** Upon merging into `main`, the deployment pipeline extracts the PR Title to name the GitHub Release, reads the specific Markdown block of that version to write the Release Description, and flags it as a "Prerelease" in GitHub if the tag contains the `-prerelease` suffix.

## Workflow Execution Summary
- **On Pull Request:** Verifies `CHANGELOG.md` changes -> Validates regex pattern of the header -> Ensures tag uniqueness via GitHub API -> Blocks merge if any check fails.
- **On Push (Merge to main):** Re-verifies uniqueness -> Creates Git Tag -> Creates GitHub Release using the PR Title and the extracted Changelog section body.