# Changelog
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

---

## [v1.2.0] - 2026-10-11

### Added
- Configurable Core and Web authentication IP limits, account limits, rate windows, and concurrency limits in Helm and Docker Compose.
- Web trusted proxy configuration through Helm `web.trustedProxies` and Compose `WEB_TRUSTED_PROXIES`.
- Compose image tag overrides through `CORE_IMAGE_TAG` and `WEB_IMAGE_TAG`.
- `docker-compose.build.yml` for building sibling Core and Web source repositories with separate local image names.
- CI configuration validation and YAML linting for the Compose build override.

### Changed
- Pinned default Helm and Compose images to Core `v1.6.0` and Web `v1.4.0`.
- Docker Compose now uses released GHCR images by default; local source builds require the `docker-compose.build.yml` override.
- Bumped the unified Helm chart from `0.2.0` to `0.3.0` and updated chart application metadata to identify both component versions.
- Expanded `.env.example` with image tags, authentication limits, trusted proxy settings, and maintenance notice options.
- Updated deployment documentation with released-image startup, local builds, authentication configuration, Core migrations 6 and 7, and Core-first upgrade steps.

### Fixed
- No fixes in this release.

### Removed
- No removals in this release.

## [v1.1.0] - 2026-06-26

### Added
- Added Helm ConfigMap support for the web maintenance notice.
- Added `web.maintenanceNotice` chart values for planned downtime banner configuration.
- Added `MAINTENANCE_NOTICE_FILE` wiring to the web deployment.
- Added Docker Compose environment variables for local maintenance notice testing.
- Added optional core gRPC TLS Helm values and secret mount support.
- Added optional web-to-core gRPC TLS chart values for future secure internal service communication.
- Added `.clineignore` for local agent/tooling hygiene.

### Changed
- Bumped unified Helm chart version from `0.1.0` to `0.2.0`.
- Updated deployment README with maintenance notice configuration notes.

### Fixed
- No fixes in this release.

### Removed
- No removals in this release.

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
