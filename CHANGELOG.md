# Changelog
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

---

## [v1.3.0] - 2026-11-13

### Added
- (fill)

### Changed
- (fill)

### Fixed
- (fill)

### Removed
- (fill)

## [Unreleased]

### Added

- Persistent Web CSRF Secret references, optional chart-managed keys, and restart checksums for explicit key rotation.
- Complete Web-to-Core TLS environment variables and CA mounts, explicit plaintext opt-ins, external Core addresses, and production configuration validation.
- Configurable Web HTTP request limits and shutdown timeouts in Helm and Compose.
- Verified Core TLS Compose override and production/development Helm example values.
- Regression checks for rendered Helm resources, invalid production settings, Secret stability, TLS mounts, and Compose configuration.

### Changed

- Helm chart version is now `0.4.0`, with Core and Web images pinned to `v2.0.0`.
- Production Helm installs require a CSRF secret and an explicit transport choice; development HTTP remains available through the development example.
- Replaced the weak bootstrap password example with a policy-compatible placeholder and documented production secret setup.
- Expanded upgrade guidance for migration `000008_resource_limits`, Core-first rollout, password/session changes, ingress HTTPS/HSTS, and the Web pagination limitation.
- CI and release chart validation use explicit environment values; release PRs also run deployment CI.
- Disabled the obsolete maintenance banner by default and removed its expired message.
- Standardized text line endings for cross-platform YAML linting and restored earlier release changelog entries from stable.

### Fixed

- Web's existing Core TLS values now reach the container and mount the configured CA.
- Prevented production startup failures caused by missing CSRF/transport wiring and avoided regenerating CSRF keys on Helm upgrades.
- Rendered numeric request body limits as decimal integers rather than scientific notation.

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
