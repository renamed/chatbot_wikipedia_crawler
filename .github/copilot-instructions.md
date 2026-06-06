# Repository Rules & Versioning Guidelines

You must adhere to the following rules when suggesting code modifications, creating pull requests, or updating documentation in this repository.

## Changelog Policy
Every pull request that changes runtime behavior, fixes a bug, or modifies choreography definitions **MUST** update the `CHANGELOG.md` file at the root of the repository. If `CHANGELOG.md` does not exist, is empty, or contains malformed release sections, create a new top-level release section in the required `## vX.Y.Z` or `## vX.Y.Z-prerelease.N` format before updating the changelog.

If the change type is unclear, classify it using this rule: update the changelog when the PR changes runtime behavior, fixes a bug, or modifies choreography definitions; otherwise do not update the changelog.

### Versioning Format
New versions must be added as a level 2 Markdown header (`##`) and must strictly follow one of these patterns:
- **Production Releases:** `## vX.Y.Z` (e.g., `## v1.0.4`)
- **Prereleases:** `## vX.Y.Z-prerelease.N` (e.g., `## v0.1.0-prerelease.1`)

When creating a new release entry, increment the version using semantic versioning: patch for bug fixes, minor for backward-compatible features, and major for breaking changes. Do not invent a version number; use the next appropriate version based on the change type.

Failure to use this exact syntax will break the automated release scripts.

### Release Body Strategy
The content directly beneath the latest release heading, whether `## vX.Y.Z` or `## vX.Y.Z-prerelease.N`, until the next `##` or EOF, is automatically extracted by GitHub Actions to populate the GitHub Release notes. Always structure the internal bullet points clearly (e.g., using `### Added`, `### Fixed`, `### Changed`).