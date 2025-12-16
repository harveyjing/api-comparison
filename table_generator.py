"""Table generator for API comparison results."""

import json
from typing import Dict, Any, List
from urllib.parse import urlparse
from har_parser import parse_har_file, group_apis_by_endpoint
from comparison_engine import compare_request_structures, compare_response_structures
from report_generator import format_differences, format_header_comparison


def format_json_for_table(value: Any) -> str:
    """Format JSON value as code block for table cell."""
    if value is None:
        return "`null`"
    if isinstance(value, dict):
        if not value:
            return "`{}`"
        # Format as JSON code block
        json_str = json.dumps(value, indent=2)
        return f"```json\n{json_str}\n```"
    if isinstance(value, list):
        if not value:
            return "`[]`"
        # Format as JSON code block
        json_str = json.dumps(value, indent=2)
        return f"```json\n{json_str}\n```"
    if isinstance(value, str):
        # If it's a long string, keep it as is but wrap in backticks
        return f"`{value}`"
    return f"`{value}`"


def extract_url_path(url: str) -> str:
    """Extract path from URL, ignoring hostname and schema."""
    parsed = urlparse(url)
    # Return path with query string if present
    if parsed.query:
        return f"{parsed.path}?{parsed.query}"
    return parsed.path


def format_request_for_table(entry: Dict[str, Any]) -> str:
    """Format request for table cell display."""
    parts = []
    
    # URL (only path, no schema/host)
    url = entry.get('original_url', '')
    if url:
        url_path = extract_url_path(url)
        parts.append(f"**URL:** `{url_path}`")
    
    # Method
    method = entry.get('method', '')
    if method:
        parts.append(f"**Method:** `{method}`")
    
    # Headers
    headers = entry.get('request', {}).get('headers', {})
    if headers:
        parts.append("**Headers:**")
        parts.append(format_json_for_table(headers))
    
    # Body
    body = entry.get('request', {}).get('body')
    if body:
        parts.append("**Body:**")
        parts.append(format_json_for_table(body))
    
    if not parts:
        return "*No request data*"
    
    return "\n\n".join(parts)


def format_response_for_table(entry: Dict[str, Any]) -> str:
    """Format response for table cell display."""
    parts = []
    
    # Status code
    status = entry.get('response', {}).get('status', 0)
    if status:
        parts.append(f"**Status:** `{status}`")
    
    # Headers
    headers = entry.get('response', {}).get('headers', {})
    if headers:
        parts.append("**Headers:**")
        parts.append(format_json_for_table(headers))
    
    # Body
    body = entry.get('response', {}).get('body')
    if body:
        parts.append("**Body:**")
        parts.append(format_json_for_table(body))
    
    if not parts:
        return "*No response data*"
    
    return "\n\n".join(parts)


def format_comments(
    legacy_entry: Dict[str, Any],
    nextgen_entry: Dict[str, Any],
    request_diff: Dict[str, Any] = None,
    response_diff: Dict[str, Any] = None,
) -> str:
    """Format differences as comments for the table."""
    comments = []
    
    # Compare requests
    if request_diff is None:
        request_diff = compare_request_structures(legacy_entry, nextgen_entry)
    
    # Method differences
    if not request_diff.get('method_identical'):
        comments.append("- **Request Method:** Methods differ")
    
    # Request header differences
    if not request_diff['headers'].get('identical'):
        header_comp = format_header_comparison(request_diff['headers'])
        if header_comp and header_comp != "Headers are identical":
            comments.append("- **Request Headers:**")
            # Format as bullet points
            for line in header_comp.split('\n'):
                if line.strip():
                    comments.append(f"  {line}")
    
    # Request body differences
    if request_diff.get('body'):
        comments.append("- **Request Body:**")
        body_diffs = format_differences(request_diff['body'])
        for line in body_diffs.split('\n'):
            if line.strip():
                comments.append(f"  {line}")
    
    # Compare responses
    if response_diff is None:
        response_diff = compare_response_structures(legacy_entry, nextgen_entry)
    
    # Status code differences
    if not response_diff['status'].get('identical'):
        legacy_status = response_diff['status'].get('legacy', 'N/A')
        nextgen_status = response_diff['status'].get('nextgen', 'N/A')
        comments.append(f"- **Response Status:** Legacy `{legacy_status}` → Nextgen `{nextgen_status}`")
    
    # Response header differences
    if not response_diff['headers'].get('identical'):
        header_comp = format_header_comparison(response_diff['headers'])
        if header_comp and header_comp != "Headers are identical":
            comments.append("- **Response Headers:**")
            for line in header_comp.split('\n'):
                if line.strip():
                    comments.append(f"  {line}")
    
    # Response body differences
    if response_diff.get('body'):
        comments.append("- **Response Body:**")
        body_diffs = format_differences(response_diff['body'])
        for line in body_diffs.split('\n'):
            if line.strip():
                comments.append(f"  {line}")
    
    if not comments:
        return "✅ No differences"
    
    return "\n".join(comments)


def format_cell_content(text: str) -> str:
    """Format text for HTML table cell, preserving code blocks and converting markdown."""
    import html
    import re
    
    lines = text.split('\n')
    result = []
    in_code_block = False
    code_block_lines = []
    
    def convert_markdown_to_html(line: str) -> str:
        """Convert markdown formatting to HTML after escaping."""
        # First escape HTML special characters
        escaped = html.escape(line)
        # Then convert markdown to HTML (on the escaped text)
        # Convert **bold** to <strong>bold</strong>
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
        # Convert `code` to <code>code</code> (but not inside <code> tags)
        escaped = re.sub(r'`([^`<]+)`', r'<code>\1</code>', escaped)
        return escaped
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            # End current code block if we're in one
            if in_code_block:
                # Close the code block
                code_content = '\n'.join(code_block_lines)
                result.append(f'<pre><code class="language-json">{html.escape(code_content)}</code></pre>')
                code_block_lines = []
                in_code_block = False
            else:
                # Start new code block
                in_code_block = True
                # Skip the ```json line
        elif in_code_block:
            code_block_lines.append(line)
        else:
            # Regular line - convert markdown to HTML
            if line.strip():
                converted = convert_markdown_to_html(line)
                result.append(converted)
            else:
                result.append('')
    
    # Handle case where code block is at the end
    if in_code_block and code_block_lines:
        code_content = '\n'.join(code_block_lines)
        result.append(f'<pre><code class="language-json">{html.escape(code_content)}</code></pre>')
    
    return '<br>'.join(result) if result else ''


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
    
    # Group by endpoint
    legacy_grouped = group_apis_by_endpoint(legacy_entries)
    nextgen_grouped = group_apis_by_endpoint(nextgen_entries)
    
    # Find common endpoints
    common_endpoints = set(legacy_grouped.keys()) & set(nextgen_grouped.keys())
    
    if not common_endpoints:
        return "# API Comparison Table\n\nNo common endpoints found.\n"
    
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
    for endpoint in sorted(common_endpoints):
        legacy_entry = legacy_grouped[endpoint][0]  # Use first occurrence
        nextgen_entry = nextgen_grouped[endpoint][0]  # Use first occurrence
        
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
        comments = format_comments(
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
        comments_cell = format_cell_content(comments)
        
        # Create table row
        lines.append('<tr>')
        lines.append(f'<td>{str(changed)}</td>')
        lines.append(f'<td>{legacy_request_cell}</td>')
        lines.append(f'<td>{nextgen_request_cell}</td>')
        lines.append(f'<td>{legacy_response_cell}</td>')
        lines.append(f'<td>{nextgen_response_cell}</td>')
        lines.append(f'<td>{comments_cell}</td>')
        lines.append('</tr>')
    
    lines.append('</tbody>')
    lines.append('</table>')
    
    return "\n".join(lines)


def main():
    """Main entry point for table generation."""
    import os
    import sys
    from pathlib import Path
    
    # Get project root directory
    project_root = Path(__file__).parent
    
    # Define file paths
    legacy_file = project_root / 'materials' / 'legacy'
    nextgen_file = project_root / 'materials' / 'nextgen'
    output_dir = project_root / 'out'
    output_file = output_dir / 'comparison_table.md'
    
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
    
    # Generate table
    print("\nGenerating comparison table...")
    table = generate_comparison_table(str(legacy_file), str(nextgen_file))
    
    # Save table
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(table)
    
    print(f"\nTable saved to: {output_file}")


if __name__ == '__main__':
    main()

