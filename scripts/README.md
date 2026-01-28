# Development Scripts

**Usage**: Most scripts are integrated into the Makefile:
- `make dev` - Start development server
- `make changelog` - Generate changelog
- `./restore_production_backup.sh --help` - Backup/restore options
- `make db-migrate` and `make db-upgrade` instead of direct script calls

## Direct Usage

If you need to run scripts directly:

```bash
# Run from project root
./scripts/script_name.py

# Or with UV for Python scripts
uv run ./scripts/script_name.py
```
