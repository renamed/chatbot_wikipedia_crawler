# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.1.0-prerelease.7

2026-06-06

### Modified
- forces use of `Automation_PAT`

## v0.1.0-prerelease.6

2026-06-06

### Fixes
- fixes version interpolation

## v0.1.0-prerelease.5

2026-06-06

### Fixes
- fixes `pyproject.toml` file location in workflows

## v0.1.0-prerelease.4

2026-06-06

### Added
- workflow logic to automatically update `pyproject.toml` version file according to `CHANGELOG.md`.

### Modified
- workflow logic refactored to ignore PRs with only `pyproject.toml` file.

## v0.1.0-prerelease.3

2026-06-06

### Modified
- now uses pr tag as the release title

## v0.1.0-prerelease.2

2026-06-06

### Fixed
- Fixed PR title extraction from workflow

## v0.1.0-prerelease.1

2026-06-06

### Added
- Initial repo setup
    - created `.gitignore` file
    - created `CHANGELOG.md` file
    - created `package.json` file
    - created `README.md` file
    - created necessary workflows
    - created `augment-context.md` file
    - created `copilot-instructions.md` file