#!/usr/bin/env python3
"""
Dependency Upgrade Scanner
Scans requirements.txt for outdated packages and reports available upgrades.
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DependencyScanner:
    """Scans Python dependencies for available upgrades."""
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        if not self.requirements_file.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_file}")
    
    def parse_requirements(self) -> List[Tuple[str, Optional[str]]]:
        """
        Parse requirements.txt and extract package names and versions.
        
        Returns:
            List of tuples (package_name, current_version)
        """
        packages = []
        
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Skip conditional dependencies
                if ';' in line:
                    line = line.split(';')[0].strip()
                
                # Extract package name and version
                # Handle formats: package>=1.0.0, package==1.0.0, package, package[extra]>=1.0.0
                match = re.match(r'^([a-zA-Z0-9_-]+(?:\[[\w,]+\])?)\s*([>=<~!]+)?\s*([0-9.]+)?', line)
                if match:
                    package_name = match.group(1)
                    version = match.group(3)
                    packages.append((package_name, version))
        
        return packages
    
    def get_latest_version(self, package_name: str) -> Optional[str]:
        """
        Get the latest version of a package from PyPI.
        
        Args:
            package_name: Name of the package (may include extras like 'package[extra]')
        
        Returns:
            Latest version string or None if not found
        """
        # Remove extras from package name for PyPI lookup
        base_package = re.sub(r'\[.*?\]', '', package_name)
        
        try:
            url = f"https://pypi.org/pypi/{base_package}/json"
            req = urllib.request.Request(url, headers={'User-Agent': 'DependencyScanner/1.0'})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data['info']['version']
        except urllib.error.HTTPError as e:
            if e.code != 404:  # Only warn for non-404 errors
                print(f"Warning: Could not fetch version for {base_package}: HTTP {e.code}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not fetch version for {base_package}: {e}", file=sys.stderr)
        
        return None
    
    def compare_versions(self, current: Optional[str], latest: Optional[str]) -> str:
        """
        Compare current and latest versions.
        
        Returns:
            Status: "up-to-date", "upgrade-available", "unknown"
        """
        if not current or not latest:
            return "unknown"
        
        # Simple version comparison (works for most semver)
        current_parts = [int(x) for x in current.split('.') if x.isdigit()]
        latest_parts = [int(x) for x in latest.split('.') if x.isdigit()]
        
        # Pad to same length
        max_len = max(len(current_parts), len(latest_parts))
        current_parts += [0] * (max_len - len(current_parts))
        latest_parts += [0] * (max_len - len(latest_parts))
        
        if latest_parts > current_parts:
            return "upgrade-available"
        elif latest_parts == current_parts:
            return "up-to-date"
        else:
            return "unknown"
    
    def scan(self) -> List[Dict]:
        """
        Scan all dependencies and check for upgrades.
        
        Returns:
            List of dictionaries with package info and upgrade status
        """
        packages = self.parse_requirements()
        results = []
        
        print(f"Scanning {len(packages)} packages from {self.requirements_file}...")
        print()
        
        for package_name, current_version in packages:
            latest_version = self.get_latest_version(package_name)
            status = self.compare_versions(current_version, latest_version)
            
            result = {
                'package': package_name,
                'current': current_version or 'not specified',
                'latest': latest_version or 'unknown',
                'status': status
            }
            results.append(result)
        
        return results
    
    def print_report(self, results: List[Dict], show_all: bool = False):
        """
        Print a formatted report of scan results.
        
        Args:
            results: List of scan results
            show_all: If True, show all packages. If False, only show upgrades.
        """
        # Filter results if not showing all
        if not show_all:
            results = [r for r in results if r['status'] == 'upgrade-available']
        
        if not results:
            print("✓ All packages are up to date!")
            return
        
        # Calculate column widths
        max_package = max(len(r['package']) for r in results)
        max_current = max(len(str(r['current'])) for r in results)
        max_latest = max(len(str(r['latest'])) for r in results)
        
        # Print header
        header = f"{'Package':<{max_package}}  {'Current':<{max_current}}  {'Latest':<{max_latest}}  Status"
        print(header)
        print('-' * len(header))
        
        # Print results
        upgrades_available = 0
        for r in results:
            status_symbol = '⬆' if r['status'] == 'upgrade-available' else '✓' if r['status'] == 'up-to-date' else '?'
            print(f"{r['package']:<{max_package}}  {r['current']:<{max_current}}  {r['latest']:<{max_latest}}  {status_symbol} {r['status']}")
            
            if r['status'] == 'upgrade-available':
                upgrades_available += 1
        
        # Print summary
        print()
        print(f"Summary: {upgrades_available} package(s) have upgrades available")
    
    def save_json(self, results: List[Dict], output_file: str):
        """Save results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Scan Python dependencies for available upgrades"
    )
    parser.add_argument(
        '--requirements',
        '-r',
        default='requirements.txt',
        help='Path to requirements.txt file (default: requirements.txt)'
    )
    parser.add_argument(
        '--all',
        '-a',
        action='store_true',
        help='Show all packages, not just those with upgrades available'
    )
    parser.add_argument(
        '--json',
        '-j',
        metavar='OUTPUT_FILE',
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    try:
        scanner = DependencyScanner(args.requirements)
        results = scanner.scan()
        
        scanner.print_report(results, show_all=args.all)
        
        if args.json:
            scanner.save_json(results, args.json)
    
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
