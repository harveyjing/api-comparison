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
        
        # Combined table for all requests with full details
        lines.append("## All Requests\n")
        lines.append("| Method | Path | Legacy Query Params | NextGen Query Params | Query Params Diff | Legacy Payload | NextGen Payload | Payload Diff | Legacy Response | NextGen Response | Status Code Diff | Body Diff |")
        lines.append("|--------|------|---------------------|----------------------|-------------------|----------------|-----------------|-------------|-----------------|------------------|------------------|-----------|")
        
        # Process matched requests
        if 'matched' in json_data:
            for req in json_data['matched']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                differences = req.get('differences', {})
                
                # Reconstruct old and new values from differences
                old_qp, new_qp = self._reconstruct_query_params(differences)
                old_payload, new_payload = self._reconstruct_payload(differences)
                old_response, new_response = self._reconstruct_response(differences)
                
                old_qp_str = self._format_value_detailed(old_qp) if old_qp else "-"
                new_qp_str = self._format_value_detailed(new_qp) if new_qp else "-"
                old_payload_str = self._format_value_detailed(old_payload) if old_payload else "-"
                new_payload_str = self._format_value_detailed(new_payload) if new_payload else "-"
                old_response_str = self._format_response_detailed(old_response) if old_response else "-"
                new_response_str = self._format_response_detailed(new_response) if new_response else "-"
                
                # Format differences
                qp_diff_str = self._format_query_params_diff(differences.get('query_params', {}))
                payload_diff_str = self._format_payload_diff(differences.get('payload', {}))
                status_diff_str = self._format_status_code_diff(differences.get('response', {}))
                body_diff_str = self._format_body_diff(differences.get('response', {}))
                
                lines.append(f"| `{self._escape_table_cell(method)}` | `{self._escape_table_cell(path)}` | {old_qp_str} | {new_qp_str} | {qp_diff_str} | {old_payload_str} | {new_payload_str} | {payload_diff_str} | {old_response_str} | {new_response_str} | {status_diff_str} | {body_diff_str} |")
        
        # Process only in old
        if 'only_in_old' in json_data:
            for req in json_data['only_in_old']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                query_params = self._format_value_detailed(req.get('query_params', {})) if req.get('query_params') else "-"
                payload = self._format_value_detailed(req.get('payload')) if req.get('payload') is not None else "-"
                # Format response if available
                old_response_str = "-"
                if 'response' in req:
                    old_response_str = self._format_single_response(req['response'])
                lines.append(f"| `{self._escape_table_cell(method)}` | `{self._escape_table_cell(path)}` | {query_params} | - | No | {payload} | - | No | {old_response_str} | - | No | No |")
        
        # Process only in new
        if 'only_in_new' in json_data:
            for req in json_data['only_in_new']:
                method = req.get('method', 'N/A')
                path = req.get('path', 'N/A')
                query_params = self._format_value_detailed(req.get('query_params', {})) if req.get('query_params') else "-"
                payload = self._format_value_detailed(req.get('payload')) if req.get('payload') is not None else "-"
                # Format response if available
                new_response_str = "-"
                if 'response' in req:
                    new_response_str = self._format_single_response(req['response'])
                lines.append(f"| `{self._escape_table_cell(method)}` | `{self._escape_table_cell(path)}` | - | {query_params} | No | - | {payload} | No | - | {new_response_str} | No | No |")
        
        lines.append("")
        
        return "\n".join(lines)
    
    
    def _escape_table_cell(self, text: str) -> str:
        """Escape special characters that break markdown tables."""
        if text is None:
            return ""
        text_str = str(text)
        # Escape pipe characters (breaks column separation)
        text_str = text_str.replace('|', '\\|')
        # Replace newlines and carriage returns with spaces
        text_str = text_str.replace('\n', ' ').replace('\r', ' ')
        # Remove multiple consecutive spaces
        while '  ' in text_str:
            text_str = text_str.replace('  ', ' ')
        return text_str
    
    def _format_value_detailed(self, value: Any) -> str:
        """Format any value with full details."""
        if value is None:
            return "-"
        
        if isinstance(value, (dict, list)):
            # Convert to JSON string for full details
            try:
                json_str = json.dumps(value, indent=2, ensure_ascii=False)
                # Escape special characters for table
                json_str = self._escape_table_cell(json_str)
                return f"<pre>{json_str}</pre>"
            except (TypeError, ValueError):
                # Fallback to string representation
                value_str = str(value)
                value_str = self._escape_table_cell(value_str)
                return f"<pre>{value_str}</pre>"
        
        # For string values
        value_str = str(value)
        value_str = self._escape_table_cell(value_str)
        return f"<pre>{value_str}</pre>"
    
    def _format_query_params_diff(self, qp_diff: Dict) -> str:
        """Format query parameters differences (simple key-value pairs, not JSON)."""
        if not qp_diff:
            return "No"
        
        parts = []
        
        # Added parameters
        if 'added' in qp_diff and qp_diff['added']:
            added_items = []
            for key, value in qp_diff['added'].items():
                added_items.append(f"{key}={value}")
            if added_items:
                parts.append(f"+{', '.join(added_items)}")
        
        # Removed parameters
        if 'removed' in qp_diff and qp_diff['removed']:
            removed_items = []
            for key, value in qp_diff['removed'].items():
                removed_items.append(f"{key}={value}")
            if removed_items:
                parts.append(f"-{', '.join(removed_items)}")
        
        # Changed parameters
        if 'changed' in qp_diff and qp_diff['changed']:
            changed_items = []
            for key, change in qp_diff['changed'].items():
                if isinstance(change, dict):
                    old_val = change.get('old', '')
                    new_val = change.get('new', '')
                    changed_items.append(f"{key}: {old_val}→{new_val}")
                else:
                    changed_items.append(f"{key}: changed")
            if changed_items:
                parts.append(f"~{', '.join(changed_items)}")
        
        return "Yes: " + " | ".join(parts) if parts else "No"
    
    def _format_payload_diff(self, payload_diff: Dict) -> str:
        """Format payload differences."""
        if not payload_diff or 'json_diff' not in payload_diff:
            return "No"
        
        diff_summary = self._format_json_diff_summary(payload_diff['json_diff'])
        return "Yes: " + diff_summary if diff_summary != "-" else "No"
    
    def _format_status_code_diff(self, response_diff: Dict) -> str:
        """Format status code differences."""
        if not response_diff or 'status_code' not in response_diff:
            return "No"
        
        status = response_diff['status_code']
        old_status = status.get('old')
        new_status = status.get('new')
        
        if old_status == new_status:
            return "No"
        else:
            return f"Yes: `{old_status}` → `{new_status}`"
    
    def _format_body_diff(self, response_diff: Dict) -> str:
        """Format body differences."""
        if not response_diff or 'body' not in response_diff:
            return "No"
        
        body_diff = response_diff['body']
        if 'json_diff' not in body_diff:
            return "No"
        
        diff_summary = self._format_json_diff_summary(body_diff['json_diff'])
        return "Yes: " + diff_summary if diff_summary != "-" else "No"
    
    def _format_json_diff_summary(self, json_diff: Dict, max_depth: int = 2, current_depth: int = 0) -> str:
        """Format json_diff structure as a summary, handling nested structures."""
        if not json_diff or current_depth >= max_depth:
            return ""
        
        parts = []
        
        # Added items
        if 'added' in json_diff and json_diff['added']:
            added_items = []
            for key, value in list(json_diff['added'].items())[:3]:  # Limit to 3 items
                key_str = str(key)
                if isinstance(value, dict) and ('added' in value or 'removed' in value or 'changed' in value):
                    # Nested diff structure
                    nested = self._format_json_diff_summary(value, max_depth, current_depth + 1)
                    if nested and nested != "-":
                        added_items.append(f"{key_str}({nested})")
                    else:
                        value_str = str(value)
                        added_items.append(f"{key_str}: {value_str}")
                else:
                    value_str = str(value)
                    added_items.append(f"{key_str}: {value_str}")
            if added_items:
                parts.append(f"+{', '.join(added_items)}")
        
        # Removed items
        if 'removed' in json_diff and json_diff['removed']:
            removed_items = []
            for key, value in list(json_diff['removed'].items())[:3]:  # Limit to 3 items
                key_str = str(key)
                if isinstance(value, dict) and ('added' in value or 'removed' in value or 'changed' in value):
                    # Nested diff structure
                    nested = self._format_json_diff_summary(value, max_depth, current_depth + 1)
                    if nested and nested != "-":
                        removed_items.append(f"{key_str}({nested})")
                    else:
                        value_str = str(value)
                        removed_items.append(f"{key_str}: {value_str}")
                else:
                    value_str = str(value)
                    removed_items.append(f"{key_str}: {value_str}")
            if removed_items:
                parts.append(f"-{', '.join(removed_items)}")
        
        # Changed items
        if 'changed' in json_diff and json_diff['changed']:
            changed_items = []
            for key, change in list(json_diff['changed'].items())[:3]:  # Limit to 3 items
                key_str = str(key)
                if isinstance(change, dict):
                    # Check if it's a nested diff structure
                    if 'added' in change or 'removed' in change or ('changed' in change and isinstance(change.get('changed'), dict)):
                        nested = self._format_json_diff_summary(change, max_depth, current_depth + 1)
                        if nested and nested != "-":
                            changed_items.append(f"{key_str}({nested})")
                        else:
                            changed_items.append(f"{key_str}: changed")
                    elif 'old' in change or 'new' in change:
                        # Simple old/new change
                        old_val = str(change.get('old', ''))
                        new_val = str(change.get('new', ''))
                        changed_items.append(f"{key_str}: {old_val}→{new_val}")
                    else:
                        # Nested structure
                        nested = self._format_json_diff_summary(change, max_depth, current_depth + 1)
                        if nested and nested != "-":
                            changed_items.append(f"{key_str}({nested})")
                        else:
                            changed_items.append(f"{key_str}: changed")
                else:
                    changed_items.append(f"{key_str}: changed")
            if changed_items:
                parts.append(f"~{', '.join(changed_items)}")
        
        result = " | ".join(parts)
        return result if result else ""
    
    def _format_response_detailed(self, response: Dict) -> str:
        """Format response with full details for table display."""
        if not response:
            return "-"
        
        parts = []
        
        # Add status code if available
        if 'status_code' in response and response['status_code'] is not None:
            status = str(response['status_code'])
            status = self._escape_table_cell(status)
            parts.append(f"Status: {status}")
        
        # Add body if available
        if 'body' in response and response['body'] is not None:
            body = response['body']
            if isinstance(body, (dict, list)):
                try:
                    body_str = json.dumps(body, indent=2, ensure_ascii=False)
                    body_str = self._escape_table_cell(body_str)
                    parts.append(f"Body:<pre>{body_str}</pre>")
                except (TypeError, ValueError):
                    body_str = str(body)
                    body_str = self._escape_table_cell(body_str)
                    parts.append(f"Body:<pre>{body_str}</pre>")
            else:
                body_str = str(body)
                body_str = self._escape_table_cell(body_str)
                parts.append(f"Body:<pre>{body_str}</pre>")
        
        if not parts:
            return "-"
        
        return "<br>".join(parts)
    
    def _format_single_response(self, response: Dict) -> str:
        """Format a single response (for only_in_old/only_in_new entries)."""
        if not response:
            return "-"
        
        # Handle error responses
        if 'error' in response:
            error_msg = str(response['error'])
            error_msg = self._escape_table_cell(error_msg)
            return f"Error: {error_msg}"
        
        parts = []
        
        # Add status code if available
        if 'status_code' in response and response['status_code'] is not None:
            status = str(response['status_code'])
            status = self._escape_table_cell(status)
            parts.append(f"Status: {status}")
        
        # Add body if available
        if 'body' in response and response['body'] is not None:
            body = response['body']
            if isinstance(body, (dict, list)):
                try:
                    body_str = json.dumps(body, indent=2, ensure_ascii=False)
                    body_str = self._escape_table_cell(body_str)
                    parts.append(f"Body:<pre>{body_str}</pre>")
                except (TypeError, ValueError):
                    body_str = str(body)
                    body_str = self._escape_table_cell(body_str)
                    parts.append(f"Body:<pre>{body_str}</pre>")
            else:
                body_str = str(body)
                body_str = self._escape_table_cell(body_str)
                parts.append(f"Body:<pre>{body_str}</pre>")
        
        if not parts:
            return "-"
        
        return "<br>".join(parts)
    
    def _reconstruct_response(self, differences: Dict) -> tuple:
        """Reconstruct old and new response from differences."""
        if 'response' not in differences:
            return None, None
        
        response_diff = differences['response']
        
        old_response = {}
        new_response = {}
        
        # Status code
        if 'status_code' in response_diff and response_diff['status_code'] is not None:
            status = response_diff['status_code']
            old_response['status_code'] = status.get('old')
            new_response['status_code'] = status.get('new')
        
        # Body
        if 'body' in response_diff and response_diff['body'] is not None:
            body_diff = response_diff['body']
            old_response['body'] = body_diff.get('old')
            new_response['body'] = body_diff.get('new')
        
        return (old_response if old_response else None, new_response if new_response else None)
    
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

