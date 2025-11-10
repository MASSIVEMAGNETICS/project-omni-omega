# Dependency Upgrade Scanner

A Python script for scanning `requirements.txt` and identifying available package upgrades from PyPI.

## Features

- **Automatic Scanning**: Parses `requirements.txt` and checks PyPI for latest versions
- **Clear Reporting**: Displays current vs. latest versions with visual indicators
- **JSON Export**: Save scan results as JSON for further processing
- **Zero Dependencies**: Uses only Python standard library (urllib, json, re)
- **GitHub Actions Integration**: Automated weekly scans with issue creation

## Usage

### Basic Usage

Scan the default `requirements.txt`:

```bash
python scan_upgrades.py
```

### Show All Packages

Display all packages, not just those with upgrades:

```bash
python scan_upgrades.py --all
```

### Custom Requirements File

Scan a different requirements file:

```bash
python scan_upgrades.py --requirements path/to/requirements.txt
```

### Export to JSON

Save results to a JSON file:

```bash
python scan_upgrades.py --json upgrade_report.json
```

### Combined Options

```bash
python scan_upgrades.py --requirements requirements.txt --all --json report.json
```

## Output Format

### Console Output

```
Scanning 37 packages from requirements.txt...

Package            Current  Latest   Status
-------------------------------------------
fastapi            0.104.0  0.121.1  ⬆ upgrade-available
pydantic           2.8      2.12.4   ⬆ upgrade-available
numpy              1.26     2.3.4    ⬆ upgrade-available

Summary: 37 package(s) have upgrades available
```

**Status Indicators:**
- ⬆ `upgrade-available` - A newer version is available
- ✓ `up-to-date` - Package is on the latest version
- ? `unknown` - Could not determine version information

### JSON Output

```json
[
  {
    "package": "fastapi",
    "current": "0.104.0",
    "latest": "0.121.1",
    "status": "upgrade-available"
  },
  {
    "package": "pydantic",
    "current": "2.8",
    "latest": "2.12.4",
    "status": "upgrade-available"
  }
]
```

## GitHub Actions Workflow

The repository includes an automated workflow (`.github/workflows/dependency-scan.yml`) that:

1. **Runs weekly** (Mondays at 9:00 AM UTC)
2. **Runs on requirements.txt changes** (when pushed to main)
3. **Can be triggered manually** (via workflow_dispatch)

The workflow will:
- Scan all dependencies
- Upload a JSON report as an artifact
- Create/update an issue if upgrades are found

### Manual Trigger

Go to **Actions** → **Dependency Upgrade Scanner** → **Run workflow**

## Command-Line Options

```
usage: scan_upgrades.py [-h] [--requirements REQUIREMENTS] [--all] [--json OUTPUT_FILE]

Scan Python dependencies for available upgrades

options:
  -h, --help            show this help message and exit
  --requirements REQUIREMENTS, -r REQUIREMENTS
                        Path to requirements.txt file (default: requirements.txt)
  --all, -a             Show all packages, not just those with upgrades available
  --json OUTPUT_FILE, -j OUTPUT_FILE
                        Save results to JSON file
```

## How It Works

1. **Parse requirements.txt**: Extracts package names and current versions
   - Supports formats: `package>=1.0.0`, `package==1.0.0`, `package[extra]>=1.0.0`
   - Handles comments and blank lines
   - Processes conditional dependencies

2. **Query PyPI**: For each package, fetches the latest version from PyPI's JSON API
   - Uses `https://pypi.org/pypi/{package}/json`
   - Handles package extras (e.g., `uvicorn[standard]`)
   - Graceful error handling for network issues

3. **Compare versions**: Simple semantic version comparison
   - Splits versions into numeric components
   - Compares major.minor.patch versions
   - Returns upgrade status

4. **Report results**: Formats output as table or JSON

## Requirements

- Python 3.8 or higher
- Internet connection (to query PyPI)
- No external dependencies required

## Limitations

- Version comparison uses simple numeric comparison (works for most semver)
- Cannot determine if upgrades are breaking changes
- Requires internet access to query PyPI
- Does not check compatibility between packages
- Platform-specific packages (with `;` conditionals) are checked without considering the condition

## Best Practices

1. **Review Before Upgrading**: Always review what changed in new versions
2. **Test in Development**: Test upgrades in a dev environment first
3. **Check Breaking Changes**: Review package changelogs for breaking changes
4. **Incremental Updates**: Update packages incrementally, not all at once
5. **Run Tests**: Always run your test suite after upgrades
6. **Pin Critical Versions**: Consider pinning versions for stability

## Example Workflow

1. Run the scanner:
   ```bash
   python scan_upgrades.py --json report.json
   ```

2. Review the report and identify safe upgrades

3. Update `requirements.txt` with new versions:
   ```
   fastapi>=0.121.1
   pydantic>=2.12.4
   ```

4. Install and test:
   ```bash
   pip install -r requirements.txt
   pytest tests/
   ```

5. Commit if tests pass:
   ```bash
   git add requirements.txt
   git commit -m "Update dependencies"
   ```

## Troubleshooting

### "Could not fetch version for package"
- Check your internet connection
- Package may not exist on PyPI
- PyPI may be experiencing issues

### "Requirements file not found"
- Verify the path to your requirements.txt
- Use `--requirements` to specify the correct path

### Timeout errors
- PyPI may be slow or down
- Try again later
- Check your network connection

## Contributing

To improve the scanner:
- Add better version comparison logic
- Support additional version specifiers
- Add caching for PyPI queries
- Implement parallel package lookups
- Add support for setup.py or pyproject.toml

## License

Same as the main project.
