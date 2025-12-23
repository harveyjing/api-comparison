"""Table generator for API comparison results."""

import json
from typing import Dict, Any, List
from urllib.parse import urlparse
from libs.har_parser import parse_har_file
from libs.comparison_engine import compare_request_structures, compare_response_structures
from libs.formatter import format_differences, format_header_comparison, format_json_value


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
        parts.append(format_json_value(headers))
    
    # Body
    body = entry.get('request', {}).get('body')
    if body:
        parts.append("**Body:**")
        parts.append(format_json_value(body))
    
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
        parts.append(format_json_value(headers))
    
    # Body
    body = entry.get('response', {}).get('body')
    if body:
        parts.append("**Body:**")
        parts.append(format_json_value(body))
    
    if not parts:
        return "*No response data*"
    
    return "\n\n".join(parts)


def format_changes(
    legacy_entry: Dict[str, Any],
    nextgen_entry: Dict[str, Any],
    request_diff: Dict[str, Any] = None,
    response_diff: Dict[str, Any] = None,
) -> str:
    """Format differences as changes for the table."""
    changes = []
    
    # Compare requests
    if request_diff is None:
        request_diff = compare_request_structures(legacy_entry, nextgen_entry)
    
    # URL differences
    url_diff = request_diff.get('url', {})
    if not url_diff.get('identical', True):
        legacy_url = url_diff.get('legacy', 'N/A')
        nextgen_url = url_diff.get('nextgen', 'N/A')
        changes.append(f"- **Request URL:** Legacy `{legacy_url}` → Nextgen `{nextgen_url}`")
    
    # Method differences
    if not request_diff.get('method_identical'):
        changes.append("- **Request Method:** Methods differ")
    
    # Request header differences
    if not request_diff['headers'].get('identical'):
        header_comp = format_header_comparison(request_diff['headers'])
        if header_comp and header_comp != "Headers are identical":
            changes.append("- **Request Headers:**")
            # Format as bullet points
            for line in header_comp.split('\n'):
                if line.strip():
                    changes.append(f"  {line}")
    
    # Request body differences
    if request_diff.get('body'):
        changes.append("- **Request Body:**")
        body_diffs = format_differences(request_diff['body'])
        for line in body_diffs.split('\n'):
            if line.strip():
                changes.append(f"  {line}")
    
    # Compare responses
    if response_diff is None:
        response_diff = compare_response_structures(legacy_entry, nextgen_entry)
    
    # Status code differences
    if not response_diff['status'].get('identical'):
        legacy_status = response_diff['status'].get('legacy', 'N/A')
        nextgen_status = response_diff['status'].get('nextgen', 'N/A')
        changes.append(f"- **Response Status:** Legacy `{legacy_status}` → Nextgen `{nextgen_status}`")
    
    # Response header differences
    if not response_diff['headers'].get('identical'):
        header_comp = format_header_comparison(response_diff['headers'])
        if header_comp and header_comp != "Headers are identical":
            changes.append("- **Response Headers:**")
            for line in header_comp.split('\n'):
                if line.strip():
                    changes.append(f"  {line}")
    
    # Response body differences
    if response_diff.get('body'):
        changes.append("- **Response Body:**")
        body_diffs = format_differences(response_diff['body'])
        for line in body_diffs.split('\n'):
            if line.strip():
                changes.append(f"  {line}")
    
    if not changes:
        return "✅ No changes"
    
    return "\n".join(changes)


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

