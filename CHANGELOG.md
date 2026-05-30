# Changelog
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

---

## [v1.0.1] - 2026-05-30

### Added
- Added a license file.

### Changed
- No changes in this release.

### Fixed
- No fixes in this release.

### Removed
- No removals in this release.

## [v1.0.0] - 2026-05-30

### Added
- Unified Helm chart `charts/ournezt` to deploy PostgreSQL, `OurNeZt-core`, and `OurNeZt-web` in one release.
- Full local Docker Compose stack for `postgres`, `core`, and `web` with service wiring and bootstrap-ready env variables.
- Production-grade inline documentation comments in `charts/ournezt/values.yaml` for secrets, migrations, ingress, and scheduling controls.
- Repo workflows/templates for deploy operations, including chart lint/render validation and Helm release packaging.

### Changed
- CI and lint workflows now validate the unified `charts/ournezt` chart as the primary deployment artifact.
- README rewritten to follow the same structure/style as `OurNeZt-core`, adapted for deploy/infrastructure workflows.
- Release workflow updated to package and publish the unified Helm chart artifact.

### Fixed
- Docker Compose CI validation no longer fails when `.env` is missing by using `.env.example` in workflow checks.
- Compose variable interpolation warnings for `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` resolved with safe defaults.

### Removed
- Deprecated standalone Helm chart `charts/ournezt-postgres` and all related workflow/documentation references.
