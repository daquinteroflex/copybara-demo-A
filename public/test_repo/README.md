# Copybara Demo B - Public Mirror Repository

This repository is a **public mirror** synced from copybara-demo-A using Copybara. It contains only the public code from the source repository.

## Repository Structure

```
copybara-demo-B/
├── src/
│   └── demo_package/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

## Purpose

This repository demonstrates:

1. **Flattened Structure**: Content from `copybara-demo-A/public/test_repo/` is synced to the root of this repository
2. **Public Code Only**: Private files from demo-A never appear here
3. **Downstream Mirror**: This repo is synced from demo-A (the source of truth)
4. **Contribution Path**: Changes made here can be synced back to demo-A

## Sync Mechanism

### This Repository is Synced FROM demo-A

- **Source**: `copybara-demo-A/public/test_repo/`
- **Destination**: This repository (root)
- **Method**: Copybara workflow `public_to_mirror`

### Contributions Flow BACK to demo-A

- Changes made in this repository can be synced back to demo-A
- Demo-A remains the authoritative source of truth
- Conflicts are resolved in favor of demo-A

## Related Repository

- **copybara-demo-A**: Source of truth repository at `https://github.com/daquinteroflex/copybara-demo-A`
  - Contains private files (never synced here)
  - Contains public files in `public/test_repo/` (synced here)
  - Includes Copybara configuration and sync documentation

## Making Contributions

1. Clone this repository
2. Make your changes
3. Push to this repository
4. Changes will be synced back to demo-A's `public/test_repo/` via Copybara

**Note**: Demo-A is the source of truth. If there are conflicts, demo-A's version wins.

## What's NOT in This Repository

The following from demo-A are **intentionally excluded**:
- `private/` directory (internal files)
- Internal configuration files
- Private utilities
- Any files outside `public/test_repo/`

## Testing

This is a trial repository to validate Copybara configuration before applying to production.

**Demo package features:**
- Simple Python package structure
- Core functionality in `src/demo_package/core.py`
- Tests in `tests/test_core.py`

## Installation & Usage

```bash
# Install dependencies (if any)
uv sync

# Run tests
uv run pytest

# Use the package
uv run python -c "from demo_package import greet; print(greet('World'))"
```

## Sync Status

This repository is maintained via automated Copybara sync from copybara-demo-A.

For sync documentation and workflow details, see:
- [copybara-demo-A/SYNC_GUIDE.md](https://github.com/daquinteroflex/copybara-demo-A/blob/main/SYNC_GUIDE.md)
- [copybara-demo-A/copy.bara.sky](https://github.com/daquinteroflex/copybara-demo-A/blob/main/copy.bara.sky)
