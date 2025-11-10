"""
Tests for the dependency upgrade scanner.
"""

import json
import tempfile
from pathlib import Path
import sys
import os

# Add parent directory to path so we can import scan_upgrades
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scan_upgrades import DependencyScanner


def test_parse_requirements():
    """Test parsing of requirements.txt file."""
    # Create a temporary requirements file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("# Comment line\n")
        f.write("\n")
        f.write("fastapi>=0.104.0\n")
        f.write("pydantic==2.8\n")
        f.write("numpy\n")
        f.write("uvicorn[standard]>=0.30\n")
        temp_file = f.name
    
    try:
        scanner = DependencyScanner(temp_file)
        packages = scanner.parse_requirements()
        
        # Check we got the right number of packages (excluding comments and empty lines)
        assert len(packages) == 4, f"Expected 4 packages, got {len(packages)}"
        
        # Check package names and versions
        package_dict = dict(packages)
        assert 'fastapi' in package_dict
        assert package_dict['fastapi'] == '0.104.0'
        assert 'pydantic' in package_dict
        assert package_dict['pydantic'] == '2.8'
        assert 'numpy' in package_dict
        assert package_dict['numpy'] is None  # No version specified
        assert 'uvicorn[standard]' in package_dict
        
        print("✓ test_parse_requirements passed")
    finally:
        os.unlink(temp_file)


def test_compare_versions():
    """Test version comparison logic."""
    scanner = DependencyScanner('requirements.txt')
    
    # Test upgrade available
    assert scanner.compare_versions('1.0.0', '2.0.0') == 'upgrade-available'
    assert scanner.compare_versions('1.2.3', '1.2.4') == 'upgrade-available'
    assert scanner.compare_versions('0.1', '0.2') == 'upgrade-available'
    
    # Test up-to-date
    assert scanner.compare_versions('1.0.0', '1.0.0') == 'up-to-date'
    assert scanner.compare_versions('2.3.4', '2.3.4') == 'up-to-date'
    
    # Test unknown
    assert scanner.compare_versions(None, '1.0.0') == 'unknown'
    assert scanner.compare_versions('1.0.0', None) == 'unknown'
    
    print("✓ test_compare_versions passed")


def test_scan_produces_results():
    """Test that scanning produces results in expected format."""
    scanner = DependencyScanner('requirements.txt')
    results = scanner.scan()
    
    # Check results is a list
    assert isinstance(results, list), "Results should be a list"
    
    # Check we have results
    assert len(results) > 0, "Should have at least one result"
    
    # Check structure of first result
    if results:
        first = results[0]
        assert 'package' in first
        assert 'current' in first
        assert 'latest' in first
        assert 'status' in first
        
        # Check status is one of expected values
        assert first['status'] in ['upgrade-available', 'up-to-date', 'unknown']
    
    print(f"✓ test_scan_produces_results passed ({len(results)} packages scanned)")


def test_json_export():
    """Test JSON export functionality."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as req_file:
        req_file.write("fastapi>=0.104.0\n")
        req_file.write("pydantic>=2.8\n")
        req_temp = req_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
        json_temp = json_file.name
    
    try:
        scanner = DependencyScanner(req_temp)
        results = scanner.scan()
        scanner.save_json(results, json_temp)
        
        # Read and verify JSON
        with open(json_temp, 'r') as f:
            loaded = json.load(f)
        
        assert isinstance(loaded, list)
        assert len(loaded) > 0
        assert all('package' in item for item in loaded)
        
        print("✓ test_json_export passed")
    finally:
        os.unlink(req_temp)
        os.unlink(json_temp)


if __name__ == '__main__':
    print("Running dependency scanner tests...")
    print()
    
    test_parse_requirements()
    test_compare_versions()
    test_scan_produces_results()
    test_json_export()
    
    print()
    print("All tests passed! ✓")
