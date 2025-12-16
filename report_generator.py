"""Report generator for API comparison results."""

from typing import Dict, Any, List
from urllib.parse import urlparse


def extract_url_path(url: str) -> str:
    """Extract path from URL, ignoring hostname."""
    parsed = urlparse(url)
    # Return path with query string if present
    if parsed.query:
        return f"{parsed.path}?{parsed.query}"
    return parsed.path


def format_json_value(value: Any, indent: int = 0) -> str:
    """Format JSON value for markdown display."""
    if value is None:
        return "`null`"
    if isinstance(value, dict):
        if not value:
            return "`{}`"
        lines = ["```json"]
        import json
        lines.append(json.dumps(value, indent=2))
        lines.append("```")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return "`[]`"
        lines = ["```json"]
        import json
        lines.append(json.dumps(value, indent=2))
        lines.append("```")
        return "\n".join(lines)
    if isinstance(value, str):
        if len(value) > 100:
            return f"`{value[:100]}...` (truncated)"
        return f"`{value}`"
    return f"`{value}`"


def format_differences(differences: List[Dict[str, Any]]) -> str:
    """Format list of differences for display."""
    if not differences:
        return "No differences"
    
    lines = []
    for diff in differences:
        diff_type = diff.get('type', 'unknown')
        path = diff.get('path', 'unknown')
        
        if diff_type == 'added':
            lines.append(f"- **Added** at `{path}`:")
            lines.append(f"{format_json_value(diff.get('nextgen_value'))}")
        elif diff_type == 'removed':
            lines.append(f"- **Removed** at `{path}`:")
            lines.append(f"{format_json_value(diff.get('legacy_value'))}")
        elif diff_type == 'modified':
            lines.append(f"- **Modified** at `{path}`:")
            lines.append(f"  - Legacy:")
            lines.append(f"{format_json_value(diff.get('legacy_value'))}")
            lines.append(f"  - Nextgen:")
            lines.append(f"{format_json_value(diff.get('nextgen_value'))}")
        elif diff_type == 'type_mismatch':
            lines.append(f"- **Type mismatch** at `{path}`:")
            lines.append(f"  - Legacy type: `{diff.get('legacy')}`")
            lines.append(f"  - Nextgen type: `{diff.get('nextgen')}`")
    
    return "\n".join(lines)


def format_header_comparison(header_diff: Dict[str, Any]) -> str:
    """Format header comparison results."""
    lines = []
    
    if header_diff.get('identical'):
        return "Headers are identical"
    
    added = header_diff.get('added', {})
    removed = header_diff.get('removed', {})
    modified = header_diff.get('modified', {})
    
    if added:
        lines.append("**Added headers:**")
        for key, value in added.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("")
    
    if removed:
        lines.append("**Removed headers:**")
        for key, value in removed.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("")
    
    if modified:
        lines.append("**Modified headers:**")
        for key, changes in modified.items():
            lines.append(f"- `{key}`:")
            lines.append(f"  - Legacy: `{changes['legacy']}`")
            lines.append(f"  - Nextgen: `{changes['nextgen']}`")
        lines.append("")
    
    return "\n".join(lines).strip()


def generate_report(comparison_results: Dict[str, Any]) -> str:
    """
    Generate markdown report from comparison results.
    
    Args:
        comparison_results: Results from comparison_engine.compare_apis()
        
    Returns:
        Markdown formatted report string
    """
    summary = comparison_results['summary']
    common_endpoints = comparison_results['common_endpoints']
    legacy_only = comparison_results['legacy_only']
    nextgen_only = comparison_results['nextgen_only']
    
    lines = []
    
    # Title
    lines.append("# API Comparison Report")
    lines.append("")
    lines.append("Comparison between Legacy and Nextgen REST APIs")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Legacy APIs**: {summary['total_legacy_apis']}")
    lines.append(f"- **Total Nextgen APIs**: {summary['total_nextgen_apis']}")
    lines.append(f"- **Common APIs**: {summary['common_apis']}")
    lines.append(f"- **Legacy Only**: {summary['legacy_only']}")
    lines.append(f"- **Nextgen Only**: {summary['nextgen_only']}")
    lines.append("")
    
    # Common endpoints comparison
    if common_endpoints:
        lines.append("## Common Endpoints Comparison")
        lines.append("")
        
        for endpoint, comparison in sorted(common_endpoints.items()):
            lines.append(f"### {endpoint}")
            lines.append("")
            lines.append(f"- **Legacy URL**: `{extract_url_path(comparison['legacy_url'])}`")
            lines.append(f"- **Nextgen URL**: `{extract_url_path(comparison['nextgen_url'])}`")
            lines.append("")
            
            # Request comparison
            lines.append("#### Request Comparison")
            lines.append("")
            req_diff = comparison['request']
            
            if not req_diff.get('method_identical'):
                # Extract method from endpoint key (format: "METHOD /path")
                method = endpoint.split()[0] if endpoint else "UNKNOWN"
                lines.append(f"- **Method**: Methods differ (Legacy and Nextgen should match)")
            
            header_comp = format_header_comparison(req_diff['headers'])
            if not req_diff['headers'].get('identical'):
                lines.append("**Headers:**")
                lines.append(header_comp)
                lines.append("")
            
            if req_diff['body']:
                lines.append("**Body Differences:**")
                lines.append(format_differences(req_diff['body']))
                lines.append("")
            elif req_diff['headers'].get('identical'):
                lines.append("✅ Request structure is identical")
                lines.append("")
            
            # Response comparison
            lines.append("#### Response Comparison")
            lines.append("")
            resp_diff = comparison['response']
            
            if not resp_diff['status']['identical']:
                lines.append(f"- **Status Code**: Legacy `{resp_diff['status']['legacy']}` → Nextgen `{resp_diff['status']['nextgen']}`")
                lines.append("")
            
            header_comp = format_header_comparison(resp_diff['headers'])
            if not resp_diff['headers'].get('identical'):
                lines.append("**Headers:**")
                lines.append(header_comp)
                lines.append("")
            
            if resp_diff['body']:
                lines.append("**Body Differences:**")
                lines.append(format_differences(resp_diff['body']))
                lines.append("")
            elif resp_diff['headers'].get('identical') and resp_diff['status']['identical']:
                lines.append("✅ Response structure is identical")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Legacy only endpoints
    if legacy_only:
        lines.append("## Endpoints Only in Legacy")
        lines.append("")
        for endpoint, details in sorted(legacy_only.items()):
            lines.append(f"- **{endpoint}**")
            lines.append(f"  - URL: `{extract_url_path(details['url'])}`")
            lines.append("")
    
    # Nextgen only endpoints
    if nextgen_only:
        lines.append("## Endpoints Only in Nextgen")
        lines.append("")
        for endpoint, details in sorted(nextgen_only.items()):
            lines.append(f"- **{endpoint}**")
            lines.append(f"  - URL: `{extract_url_path(details['url'])}`")
            lines.append("")
    
    return "\n".join(lines)


