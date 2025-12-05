#!/usr/bin/env python3
"""
JSON to Markdown Converter

Converts API comparison JSON results to a human-readable Markdown format.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any


class MarkdownConverter:
    """Converts JSON comparison results to Markdown."""
    
    def __init__(self):
        pass
    
    def convert(self, json_data: Dict) -> str:
        """Convert JSON data to Markdown format."""
        lines = []
        
        # Title
        lines.append("# API Comparison Report\n")
        
        # Metadata section
        if 'metadata' in json_data:
            lines.append("## Metadata\n")
            metadata = json_data['metadata']
            lines.append("| Item | Value |")
            lines.append("|------|-------|")
            if metadata.get('old_base_url'):
                lines.append(f"| Old Base URL | `{metadata['old_base_url']}` |")
            if metadata.get('new_base_url'):
                lines.append(f"| New Base URL | `{metadata['new_base_url']}` |")
            if metadata.get('old_auth_token'):
                token = metadata['old_auth_token']
                # Truncate token for display
                token_display = token[:50] + "..." if len(token) > 50 else token
                lines.append(f"| Old Auth Token | `{token_display}` |")
            if metadata.get('new_auth_token'):
                token = metadata['new_auth_token']
                token_display = token[:50] + "..." if len(token) > 50 else token
                lines.append(f"| New Auth Token | `{token_display}` |")
            lines.append("")
        
        # Summary section
        if 'summary' in json_data:
            lines.append("## Summary\n")
            summary = json_data['summary']
            lines.append("| Metric | Count |")
            lines.append("|--------|-------|")
            lines.append(f"| Total Requests (Old) | {summary.get('total_old', 0)} |")
            lines.append(f"| Total Requests (New) | {summary.get('total_new', 0)} |")
            lines.append(f"| Matched Requests | {summary.get('matched', 0)} |")
            lines.append(f"| Only in Old | {summary.get('only_in_old', 0)} |")
            lines.append(f"| Only in New | {summary.get('only_in_new', 0)} |")
            lines.append("")
        
        # Combined table for all requests
        lines.append("## All Requests\n")
        lines.append("| Method | Path | Old Query Params | Old Payload | New Query Params | New Payload | Differences |")
        lines.append("|--------|------|------------------|-------------|------------------|-------------|-------------|")
        
        # Process matched requests
        if 'matched' in json_data:
            for req in json_data['matched']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                differences = req.get('differences', {})
                has_diffs = req.get('has_differences', False)
                
                # Reconstruct old and new values from differences
                old_qp, new_qp = self._reconstruct_query_params(differences)
                old_payload, new_payload = self._reconstruct_payload(differences)
                
                # Format differences summary
                diff_summary = self._format_diff_summary(differences) if has_diffs else "-"
                
                old_qp_str = self._format_query_params(old_qp) if old_qp else "-"
                new_qp_str = self._format_query_params(new_qp) if new_qp else "-"
                old_payload_str = self._format_payload(old_payload) if old_payload else "-"
                new_payload_str = self._format_payload(new_payload) if new_payload else "-"
                
                lines.append(f"| `{method}` | `{path}` | {old_qp_str} | {old_payload_str} | {new_qp_str} | {new_payload_str} | {diff_summary} |")
        
        # Process only in old
        if 'only_in_old' in json_data:
            for req in json_data['only_in_old']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                query_params = self._format_query_params(req.get('query_params', {}))
                payload = self._format_payload(req.get('payload'))
                lines.append(f"| `{method}` | `{path}` | {query_params} | {payload} | - | - | Only in Old |")
        
        # Process only in new
        if 'only_in_new' in json_data:
            for req in json_data['only_in_new']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                query_params = self._format_query_params(req.get('query_params', {}))
                payload = self._format_payload(req.get('payload'))
                lines.append(f"| `{method}` | `{path}` | - | - | {query_params} | {payload} | Only in New |")
        
        lines.append("")
        
        # Detailed differences for matched requests with differences
        if 'matched' in json_data:
            with_diffs = [r for r in json_data['matched'] if r.get('has_differences', False)]
            if with_diffs:
                lines.append("## Detailed Differences\n")
                for req in with_diffs:
                    lines.extend(self._format_request_with_differences(req))
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_request_with_differences(self, req: Dict) -> List[str]:
        """Format a request with its differences in table format."""
        lines = []
        
        method = req.get('method', 'N/A')
        path = req.get('path', 'N/A')
        differences = req.get('differences', {})
        
        lines.append(f"### `{method} {path}`\n")
        
        # Path differences
        if 'path' in differences:
            path_diff = differences['path']
            lines.append("**Path Difference:**")
            lines.append("| Old | New |")
            lines.append("|-----|-----|")
            old_path = path_diff.get('old', 'N/A')
            new_path = path_diff.get('new', 'N/A')
            lines.append(f"| `{old_path}` | `{new_path}` |")
            lines.append("")
        
        # Query parameter differences
        if 'query_params' in differences:
            qp_diff = differences['query_params']
            lines.append("**Query Parameter Differences:**")
            
            # Collect all differences for table
            table_rows = []
            
            if 'added' in qp_diff and qp_diff['added']:
                for key, value in qp_diff['added'].items():
                    table_rows.append(('Added', key, '-', self._format_value_for_table(value)))
            
            if 'removed' in qp_diff and qp_diff['removed']:
                for key, value in qp_diff['removed'].items():
                    table_rows.append(('Removed', key, self._format_value_for_table(value), '-'))
            
            if 'changed' in qp_diff and qp_diff['changed']:
                for key, change in qp_diff['changed'].items():
                    old_val = self._format_value_for_table(change.get('old'))
                    new_val = self._format_value_for_table(change.get('new'))
                    table_rows.append(('Changed', key, old_val, new_val))
            
            if table_rows:
                lines.append("| Type | Parameter | Old Value | New Value |")
                lines.append("|------|-----------|-----------|-----------|")
                for row_type, key, old_val, new_val in table_rows:
                    lines.append(f"| {row_type} | `{key}` | {old_val} | {new_val} |")
                lines.append("")
        
        # Payload differences
        if 'payload' in differences:
            payload_diff = differences['payload']
            lines.append("**Payload Differences:**")
            
            if 'json_diff' in payload_diff:
                json_diff = payload_diff['json_diff']
                table_rows = []
                
                if 'added' in json_diff and json_diff['added']:
                    for key, value in json_diff['added'].items():
                        table_rows.append(('Added', key, '-', self._format_value_for_table(value)))
                
                if 'removed' in json_diff and json_diff['removed']:
                    for key, value in json_diff['removed'].items():
                        table_rows.append(('Removed', key, self._format_value_for_table(value), '-'))
                
                if 'changed' in json_diff and json_diff['changed']:
                    for key, change in json_diff['changed'].items():
                        old_val = change.get('old')
                        new_val = change.get('new')
                        old_str = self._format_value_for_table(old_val)
                        new_str = self._format_value_for_table(new_val)
                        table_rows.append(('Changed', key, old_str, new_str))
                
                if table_rows:
                    lines.append("| Type | Field | Old Value | New Value |")
                    lines.append("|------|-------|-----------|-----------|")
                    for row_type, key, old_val, new_val in table_rows:
                        lines.append(f"| {row_type} | `{key}` | {old_val} | {new_val} |")
                    lines.append("")
            else:
                # Text comparison - use table
                old_payload = payload_diff.get('old')
                new_payload = payload_diff.get('new')
                lines.append("| Old | New |")
                lines.append("|-----|-----|")
                old_str = self._format_value_for_table(old_payload)
                new_str = self._format_value_for_table(new_payload)
                lines.append(f"| {old_str} | {new_str} |")
                lines.append("")
        
        # Response differences
        if 'response' in differences:
            response_diff = differences['response']
            lines.append("**Response Differences:**")
            
            if 'error' in response_diff:
                lines.append("| Type | Message |")
                lines.append("|------|---------|")
                lines.append(f"| Error | {response_diff['error']} |")
            else:
                table_rows = []
                
                if 'status_code' in response_diff:
                    status = response_diff['status_code']
                    table_rows.append(('Status Code', 
                                     str(status.get('old', 'N/A')), 
                                     str(status.get('new', 'N/A'))))
                
                if 'body' in response_diff:
                    body_diff = response_diff['body']
                    if 'json_diff' in body_diff:
                        json_diff = body_diff['json_diff']
                        if 'added' in json_diff and json_diff['added']:
                            for key, value in json_diff['added'].items():
                                table_rows.append(('Body Field Added', key, '-', self._format_value_for_table(value)))
                        if 'removed' in json_diff and json_diff['removed']:
                            for key, value in json_diff['removed'].items():
                                table_rows.append(('Body Field Removed', key, self._format_value_for_table(value), '-'))
                        if 'changed' in json_diff and json_diff['changed']:
                            for key, change in json_diff['changed'].items():
                                old_val = self._format_value_for_table(change.get('old'))
                                new_val = self._format_value_for_table(change.get('new'))
                                table_rows.append(('Body Field Changed', key, old_val, new_val))
                    else:
                        old_body = body_diff.get('old')
                        new_body = body_diff.get('new')
                        table_rows.append(('Body', self._format_value_for_table(old_body), 
                                         self._format_value_for_table(new_body)))
                
                if table_rows:
                    if any(len(row) == 4 for row in table_rows):
                        lines.append("| Type | Field | Old Value | New Value |")
                        lines.append("|------|-------|-----------|-----------|")
                        for row in table_rows:
                            if len(row) == 4:
                                lines.append(f"| {row[0]} | `{row[1]}` | {row[2]} | {row[3]} |")
                            else:
                                lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
                    else:
                        lines.append("| Type | Old Value | New Value |")
                        lines.append("|------|-----------|-----------|")
                        for row in table_rows:
                            lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
            
            lines.append("")
        
        return lines
    
    def _format_query_params(self, params: Dict) -> str:
        """Format query parameters for table display."""
        if not params:
            return "-"
        
        parts = []
        for key, value in params.items():
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value)
            else:
                value_str = str(value)
            parts.append(f"`{key}={value_str}`")
        
        return "<br>".join(parts) if parts else "-"
    
    def _format_payload(self, payload: Any) -> str:
        """Format payload for table display."""
        if payload is None:
            return "-"
        
        if isinstance(payload, dict):
            # Show a summary
            keys = list(payload.keys())[:3]
            if len(payload) > 3:
                return f"`{len(payload)} fields: {', '.join(keys)}...`"
            return f"`{', '.join(keys)}`"
        
        payload_str = str(payload)
        if len(payload_str) > 50:
            return f"`{payload_str[:50]}...`"
        return f"`{payload_str}`"
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if value is None:
            return "null"
        
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2)
        
        return str(value)
    
    def _format_value_for_table(self, value: Any) -> str:
        """Format a value for table display (compact format)."""
        if value is None:
            return "`null`"
        
        if isinstance(value, (dict, list)):
            # For complex values, use code block in table cell
            json_str = json.dumps(value, indent=2)
            # Escape pipe characters for markdown tables
            json_str = json_str.replace('|', '\\|')
            # Truncate if too long
            if len(json_str) > 200:
                json_str = json_str[:200] + "..."
            return f"<pre>{json_str}</pre>"
        
        value_str = str(value)
        # Escape pipe and newline characters
        value_str = value_str.replace('|', '\\|').replace('\n', ' ')
        # Truncate if too long
        if len(value_str) > 100:
            value_str = value_str[:100] + "..."
        return f"`{value_str}`"
    
    def _reconstruct_query_params(self, differences: Dict) -> tuple:
        """Reconstruct old and new query params from differences."""
        if 'query_params' not in differences:
            return None, None
        
        qp_diff = differences['query_params']
        old_params = qp_diff.get('old', {})
        new_params = qp_diff.get('new', {})
        
        # If old/new are not directly available, reconstruct from added/removed/changed
        if not old_params and not new_params:
            # Start with empty dicts
            old_params = {}
            new_params = {}
            
            # Add removed params to old
            if 'removed' in qp_diff:
                old_params.update(qp_diff['removed'])
            
            # Add changed params (old values) to old
            if 'changed' in qp_diff:
                for key, change in qp_diff['changed'].items():
                    old_params[key] = change.get('old')
            
            # Build new from old + added + changed
            new_params = old_params.copy()
            if 'added' in qp_diff:
                new_params.update(qp_diff['added'])
            if 'changed' in qp_diff:
                for key, change in qp_diff['changed'].items():
                    new_params[key] = change.get('new')
        
        return old_params if old_params else None, new_params if new_params else None
    
    def _reconstruct_payload(self, differences: Dict) -> tuple:
        """Reconstruct old and new payload from differences."""
        if 'payload' not in differences:
            return None, None
        
        payload_diff = differences['payload']
        old_payload = payload_diff.get('old')
        new_payload = payload_diff.get('new')
        
        # If old/new are not directly available, try to reconstruct from json_diff
        if old_payload is None and new_payload is None and 'json_diff' in payload_diff:
            # For json_diff, we can't fully reconstruct, so return None
            # The detailed section will show the diff
            return None, None
        
        return old_payload, new_payload
    
    def _format_diff_summary(self, differences: Dict) -> str:
        """Format a summary of differences."""
        diff_types = []
        if 'path' in differences:
            diff_types.append('Path')
        if 'query_params' in differences:
            diff_types.append('Query Params')
        if 'payload' in differences:
            diff_types.append('Payload')
        if 'response' in differences:
            diff_types.append('Response')
        return ', '.join(diff_types) if diff_types else '-'


def main():
    parser = argparse.ArgumentParser(
        description='Convert API comparison JSON results to Markdown'
    )
    parser.add_argument(
        'json_file',
        type=Path,
        help='Path to JSON comparison results file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output Markdown file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Read JSON file
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Convert to Markdown
    converter = MarkdownConverter()
    markdown = converter.convert(json_data)
    
    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Markdown report written to {args.output}")
    else:
        print(markdown)


if __name__ == '__main__':
    main()

