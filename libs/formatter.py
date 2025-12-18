"""Report generator for API comparison results."""

from typing import Dict, Any, List

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
