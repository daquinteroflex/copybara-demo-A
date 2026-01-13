# Copybara Demo A - Source of Truth Repository

This repository serves as the **authoritative source** for a bidirectional Copybara sync trial between two repositories.

## Repository Structure

```
copybara-demo-A/
├── private/                    # PRIVATE - Never synced
│   ├── internal_config.py     # Internal configuration
│   └── private_utils.py       # Private utilities
├── public/                     # PUBLIC - Synced to demo-B
│   └── test_repo/             # Python package (synced to demo-B root)
│       ├── src/
│       │   └── demo_package/
│       │       ├── __init__.py
│       │       └── core.py
│       ├── tests/
│       │   └── test_core.py
│       ├── pyproject.toml
│       └── README.md
├── copy.bara.sky              # Copybara configuration
├── SYNC_GUIDE.md              # How to run Copybara sync
└── README.md                  # This file
```

## Purpose

This repository demonstrates:

1. **Private/Public File Separation**: `private/` directory contains files that never sync to the public mirror
2. **Directory Structure Transformation**: `public/test_repo/` syncs to the root of copybara-demo-B
3. **Bidirectional Sync Pattern**: Changes flow both A→B and B→A using two workflows
4. **Source of Truth**: This repository (demo-A) is authoritative for conflict resolution

## Sync Mechanism

### Workflow 1: A → B (Primary Sync)
- **Source**: `copybara-demo-A/public/test_repo/`
- **Destination**: `copybara-demo-B/` (root)
- **Purpose**: Sync public code to downstream mirror
- **Command**: `copybara copy.bara.sky public_to_mirror`

### Workflow 2: B → A (Contribution Flow)
- **Source**: `copybara-demo-B/` (root)
- **Destination**: `copybara-demo-A/public/test_repo/`
- **Purpose**: Accept external contributions back to source of truth
- **Command**: `copybara copy.bara.sky mirror_to_public`

## Key Features

- **Private files isolation**: Files in `private/` never appear in demo-B
- **Directory flattening**: `public/test_repo/*` becomes `demo-B/*`
- **Bidirectional flow**: Contributions accepted from both repos
- **Single source of truth**: Demo-A is authoritative

## Usage

See [SYNC_GUIDE.md](./SYNC_GUIDE.md) for detailed instructions on:
- Running Copybara workflows
- Testing sync in both directions
- Handling conflicts
- Verifying sync integrity

## Related Repository

- **copybara-demo-B**: Public mirror repository at `https://github.com/daquinteroflex/copybara-demo-B`
  - Contains only public files from `public/test_repo/`
  - Flattened directory structure (no `public/test_repo/` prefix)
  - Accepts external contributions

## Testing

This is a trial setup to validate Copybara configuration before applying to production repositories.

**Test scenarios:**
1. Add code in demo-A's `public/test_repo/` → sync to demo-B
2. Add code in demo-B → sync to demo-A's `public/test_repo/`
3. Verify private files never appear in demo-B
4. Test conflict resolution (demo-A wins)
