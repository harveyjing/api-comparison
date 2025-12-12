#!/usr/bin/env python3
"""Main script to compare APIs between legacy and nextgen HAR files."""

import os
import sys
from pathlib import Path
from comparison_engine import compare_apis
from report_generator import generate_report


def main():
    """Main entry point for API comparison."""
    # Get project root directory
    project_root = Path(__file__).parent
    
    # Define file paths
    legacy_file = project_root / 'materials' / 'legacy'
    nextgen_file = project_root / 'materials' / 'nextgen'
    output_dir = project_root / 'out'
    output_file = output_dir / 'comparison_report.md'
    
    # Check if input files exist
    if not legacy_file.exists():
        print(f"Error: Legacy HAR file not found at {legacy_file}", file=sys.stderr)
        sys.exit(1)
    
    if not nextgen_file.exists():
        print(f"Error: Nextgen HAR file not found at {nextgen_file}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    print("Parsing HAR files...")
    print(f"  - Legacy: {legacy_file}")
    print(f"  - Nextgen: {nextgen_file}")
    
    # Run comparison
    print("\nComparing APIs...")
    comparison_results = compare_apis(str(legacy_file), str(nextgen_file))
    
    # Generate report
    print("Generating report...")
    report = generate_report(comparison_results)
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_file}")
    
    # Print summary
    summary = comparison_results['summary']
    print("\nSummary:")
    print(f"  - Total Legacy APIs: {summary['total_legacy_apis']}")
    print(f"  - Total Nextgen APIs: {summary['total_nextgen_apis']}")
    print(f"  - Common APIs: {summary['common_apis']}")
    print(f"  - Legacy Only: {summary['legacy_only']}")
    print(f"  - Nextgen Only: {summary['nextgen_only']}")


if __name__ == '__main__':
    main()


