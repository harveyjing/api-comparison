#!/usr/bin/env python3
"""Script to process all modules and generate separate comparison tables."""

import os
import sys
from pathlib import Path
from libs.table_helper import parse_har_file, compare_request_structures, compare_response_structures, format_request_for_table, format_response_for_table, format_cell_content, format_changes
from libs.har_parser import group_apis_by_name

def find_modules(materials_dir: Path) -> list[str]:
    """
    Find all module directories in the materials directory.
    
    A valid module directory must contain both 'legacy' and 'nextgen' files.
    
    Args:
        materials_dir: Path to materials directory
        
    Returns:
        List of module names
    """
    modules = []
    
    if not materials_dir.exists():
        return modules
    
    for item in materials_dir.iterdir():
        if item.is_dir():
            legacy_file = item / 'legacy'
            nextgen_file = item / 'nextgen'
            
            # Check if both files exist
            if legacy_file.exists() and nextgen_file.exists():
                modules.append(item.name)
    
    return modules


def process_module(module_name: str, materials_dir: Path, output_dir: Path) -> bool:
    """
    Process a single module and generate its comparison table.
    
    Args:
        module_name: Name of the module
        materials_dir: Path to materials directory
        output_dir: Path to output directory
        
    Returns:
        True if successful, False otherwise
    """
    module_dir = materials_dir / module_name
    legacy_file = module_dir / 'legacy'
    nextgen_file = module_dir / 'nextgen'
    output_file = output_dir / f'comparison_table_{module_name}.md'
    
    try:
        print(f"\nProcessing module: {module_name}")
        print(f"  - Legacy: {legacy_file}")
        print(f"  - Nextgen: {nextgen_file}")
        
        # Generate table with name-based matching
        print("  Generating comparison table...")
        table = generate_comparison_table(
            str(legacy_file),
            str(nextgen_file)
        )
        
        # Save table
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(table)
        
        print(f"  ✓ Table saved to: {output_file}")
        return True
        
    except ValueError as e:
        print(f"  ✗ Error: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def generate_comparison_table(legacy_file: str, nextgen_file: str) -> str:
    """
    Generate markdown table comparing Legacy and NextGen APIs.
    
    Args:
        legacy_file: Path to legacy HAR file
        nextgen_file: Path to nextgen HAR file
        
    Returns:
        Markdown formatted table string
    """
    # Parse HAR files
    legacy_entries = parse_har_file(legacy_file)
    nextgen_entries = parse_har_file(nextgen_file)
    
    # Group by name
    legacy_grouped = group_apis_by_name(legacy_entries)
    nextgen_grouped = group_apis_by_name(nextgen_entries)
    
    # Find common keys
    common_keys = set(legacy_grouped.keys()) & set(nextgen_grouped.keys())
    
    if not common_keys:
        return "# API Comparison Table\n\nNo common keys found.\n"
    
    lines = []
    lines.append("# API Comparison Table")
    lines.append("")
    lines.append("Comparison between Legacy and Nextgen REST APIs")
    lines.append("")
    lines.append('<style>')
    lines.append('table { border-collapse: collapse; width: 100%; }')
    lines.append('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }')
    lines.append('th { background-color: #f2f2f2; }')
    lines.append('pre { margin: 0; overflow-x: auto; }')
    lines.append('code { display: block; white-space: pre; }')
    lines.append('</style>')
    lines.append("")
    
    # Use HTML table for better code block support
    lines.append('<table>')
    lines.append('<thead>')
    lines.append('<tr>')
    lines.append('<th>Changed</th>')
    lines.append('<th>Legacy Request</th>')
    lines.append('<th>NextGen Request</th>')
    lines.append('<th>Legacy Response</th>')
    lines.append('<th>NextGen Response</th>')
    lines.append('<th>Comments</th>')
    lines.append('</tr>')
    lines.append('</thead>')
    lines.append('<tbody>')
    
    # Generate rows for each common endpoint
    for key in sorted(common_keys):
        legacy_entry = legacy_grouped[key][0]  # Use first occurrence
        nextgen_entry = nextgen_grouped[key][0]  # Use first occurrence
        
        # Compute diffs once for reuse
        request_diff = compare_request_structures(legacy_entry, nextgen_entry)
        response_diff = compare_response_structures(legacy_entry, nextgen_entry)
        changed = (
            not request_diff.get('method_identical')
            or not request_diff['headers'].get('identical')
            or bool(request_diff.get('body'))
            or not response_diff['status'].get('identical')
            or not response_diff['headers'].get('identical')
            or bool(response_diff.get('body'))
        )
        
        # Format each column
        legacy_request = format_request_for_table(legacy_entry)
        nextgen_request = format_request_for_table(nextgen_entry)
        legacy_response = format_response_for_table(legacy_entry)
        nextgen_response = format_response_for_table(nextgen_entry)
        changes = format_changes(
            legacy_entry,
            nextgen_entry,
            request_diff=request_diff,
            response_diff=response_diff,
        )
        
        # Format for HTML table cells
        legacy_request_cell = format_cell_content(legacy_request)
        nextgen_request_cell = format_cell_content(nextgen_request)
        legacy_response_cell = format_cell_content(legacy_response)
        nextgen_response_cell = format_cell_content(nextgen_response)
        changes_cell = format_cell_content(changes)
        
        # Create table row
        lines.append('<tr>')
        lines.append(f'<td>{str(changed)}</td>')
        lines.append(f'<td>{legacy_request_cell}</td>')
        lines.append(f'<td>{nextgen_request_cell}</td>')
        lines.append(f'<td>{legacy_response_cell}</td>')
        lines.append(f'<td>{nextgen_response_cell}</td>')
        lines.append(f'<td>{changes_cell}</td>')
        lines.append('</tr>')
    
    lines.append('</tbody>')
    lines.append('</table>')
    
    return "\n".join(lines)


def main():
    """Main entry point for module processing."""
    # Get project root directory
    project_root = Path(__file__).parent
    
    # Define directories
    materials_dir = project_root / 'materials'
    output_dir = project_root / 'out'
    
    # Check if materials directory exists
    if not materials_dir.exists():
        print(f"Error: Materials directory not found at {materials_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Find all modules
    print("Scanning for modules...")
    modules = find_modules(materials_dir)
    
    if not modules:
        print("No modules found. A module directory must contain both 'legacy' and 'nextgen' files.")
        sys.exit(1)
    
    print(f"Found {len(modules)} module(s): {', '.join(modules)}")
    
    # Process each module
    success_count = 0
    for module_name in modules:
        if process_module(module_name, materials_dir, output_dir):
            success_count += 1
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(modules)} module(s) processed successfully")
    
    if success_count < len(modules):
        sys.exit(1)


if __name__ == '__main__':
    main()
