# AI Agent Platform SDK CI/CD Setup

This document describes the CI/CD configuration for the `ai-agent-platform-sdk` package.

## Overview

The SDK uses a **package-based CI/CD approach** rather than Docker-based deployment, since it's a Python package that gets published to package registries.

## CI/CD Options

### 1. Google Cloud Build (Primary)

#### Files:
- `cloudbuild.yml` - Main build pipeline for releases
- `cloudbuild-pr.yml` - Pull request testing pipeline
- `build.ci.sh` - Build script for local/CI execution
- `build.ci.env` - Environment variables configuration

#### Main Pipeline (`cloudbuild.yml`):
1. **Install Dependencies** - Install Poetry and dependencies
2. **Run Pre-commit** - Code quality checks
3. **Run Tests** - Execute test suite with coverage
4. **Update Version** - Auto-version based on git tags or build numbers
5. **Build Package** - Create distributable package
6. **Publish to Registry** - Publish to configured package registry

#### PR Pipeline (`cloudbuild-pr.yml`):
1. **Install Dependencies** - Install Poetry and dependencies
2. **Run Pre-commit** - Code quality checks
3. **Run Tests** - Execute test suite with coverage
4. **Build Package (Test)** - Build package for validation only
5. **Run SCA** - Security and code analysis

### 2. GitHub Actions (Alternative)

#### File:
- `.github/workflows/ci.yml` - GitHub Actions workflow

#### Features:
- Automated testing on push/PR
- Release-based versioning and publishing
- PyPI publishing on releases
- Code coverage reporting

## Key Differences from Docker Applications

| Aspect | Docker Applications | SDK Package |
|--------|-------------------|-------------|
| **Build Output** | Docker image | Python package (wheel/sdist) |
| **Deployment** | Container registry | Package registry (PyPI, private) |
| **Versioning** | Image tags | Package version in pyproject.toml |
| **CI Focus** | Image building, testing | Package building, testing, publishing |

## Version Management

### Automatic Versioning:
- **Release builds**: Uses git tag (e.g., `v1.2.3` → version `1.2.3`)
- **CI builds**: Appends build number to current version (e.g., `1.2.3.abc123`)

### Version Commands:
```bash
# Check current version
poetry version -s

# Set specific version
poetry version 1.2.3

# Bump patch/minor/major
poetry version patch
poetry version minor
poetry version major
```

## Package Publishing

### Private Registry:
- Configured to publish to Google Artifact Registry
- Uses `POETRY_REGISTRY_TOKEN` secret
- Registry: `asia-southeast2-docker.pkg/${PROJECT_ID}/projects`

### PyPI (GitHub Releases):
- Automatic publishing on GitHub releases
- Uses `PYPI_TOKEN` secret
- Only publishes release versions (not CI builds)

## Local Development

### Running CI Locally:
```bash
cd ai-agent-platform-sdk
./build.ci.sh
```

### Manual Package Building:
```bash
poetry install --with dev
poetry run pre-commit run --all-files
poetry run python -m pytest tests/ -v --cov=glaip_sdk --cov-report=term-missing --cov-report=xml --cov-fail-under=90
poetry build
```

## Environment Variables

### Required for CI/CD:
- `CI=true` - Enables CI mode
- `BUILD_NUMBER` - Build identifier
- `TAG_NAME` - Git tag for releases
- `POETRY_TOKEN` - Registry authentication

### Optional:
- `VERSION_NUMBER` - Custom version override
- `POETRY_REGISTRY_URL` - Custom registry URL

## Testing Strategy

### Test Coverage:
- **Minimum**: 90% coverage required
- **Reports**: XML (for CI) + HTML (for local development)
- **Parallel**: Tests run in parallel for faster execution

### Quality Gates:
- Pre-commit hooks must pass
- All tests must pass
- Coverage threshold must be met
- Security analysis must pass

## Troubleshooting

### Common Issues:
1. **Poetry not found**: Install Poetry via `curl -sSL https://install.python-poetry.org | python3 -`
2. **Coverage below threshold**: Add tests to increase coverage
3. **Pre-commit failures**: Run `poetry run pre-commit run --all-files` locally first
4. **Version conflicts**: Check `pyproject.toml` and git tags

### Debug Commands:
```bash
# Check Poetry configuration
poetry config --list

# Verify package structure
poetry show --tree

# Test package installation
pip install dist/*.whl
```

## Integration with Main Platform

The SDK CI/CD is **independent** of the main platform's Docker-based CI/CD:
- Runs separately from `ai-agent-platform-backend` and `ai-agent-platform-runner`
- Focuses on package quality and publishing
- Integrates with the same security and quality tools
- Shares the same project configuration and secrets
