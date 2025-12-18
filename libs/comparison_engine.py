"""API comparison engine for comparing legacy and nextgen APIs."""

from typing import Dict, List, Any, Set, Tuple
from libs.har_parser import group_apis_by_name, parse_har_file
import json


def extract_structure(obj: Any) -> Any:
    """
    Extract structural representation of a JSON object, ignoring values.
    
    Args:
        obj: JSON object to extract structure from
        
    Returns:
        Structural representation (types, keys, nested structures)
    """
    if obj is None:
        return "NoneType"
    
    if isinstance(obj, dict):
        # Extract keys and recursively extract structure of values
        return {key: extract_structure(value) for key, value in obj.items()}
    
    if isinstance(obj, list):
        # Extract structure of first item (if list is non-empty), ignore length
        if len(obj) > 0:
            return [extract_structure(obj[0])]
        else:
            return []
    
    # For primitives, return the type name only (not the value)
    return type(obj).__name__


def extract_common_list_structure(items: List[Any]) -> Any:
    """
    Extract the common structure from a list of items using majority approach.
    Analyzes all items to find the most common type and structure.
    
    Args:
        items: List of items to analyze
        
    Returns:
        Common structural representation of the list items
    """
    if len(items) == 0:
        return []
    
    # Count type occurrences
    type_counts: Dict[str, int] = {}
    type_items: Dict[str, List[Any]] = {}
    
    for item in items:
        item_type = type(item).__name__
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
        if item_type not in type_items:
            type_items[item_type] = []
        type_items[item_type].append(item)
    
    # Find most common type
    most_common_type = max(type_counts.items(), key=lambda x: x[1])[0]
    most_common_items = type_items[most_common_type]
    
    # Extract structure based on most common type
    if most_common_type == 'dict':
        # For dictionaries, find keys present in majority of items
        key_counts: Dict[str, int] = {}
        key_structures: Dict[str, List[Any]] = {}
        
        for item in most_common_items:
            for key, value in item.items():
                key_counts[key] = key_counts.get(key, 0) + 1
                if key not in key_structures:
                    key_structures[key] = []
                key_structures[key].append(value)
        
        # Include keys present in majority (more than 50%)
        majority_threshold = len(most_common_items) / 2
        common_structure = {}
        
        for key, count in key_counts.items():
            if count > majority_threshold:
                # Extract common structure for this key's values
                values = key_structures[key]
                if len(values) > 0:
                    # If all values have same type, use that structure
                    value_types = [type(v).__name__ for v in values]
                    most_common_value_type = max(set(value_types), key=value_types.count)
                    
                    # Get items with most common value type
                    same_type_values = [v for v in values if type(v).__name__ == most_common_value_type]
                    
                    if most_common_value_type == 'dict':
                        # Recursively extract common structure for nested dicts
                        common_structure[key] = extract_common_list_structure(same_type_values)
                    elif most_common_value_type == 'list':
                        # Extract common structure for nested lists
                        common_structure[key] = extract_common_list_structure(same_type_values)
                    else:
                        # For primitives, just use the type
                        common_structure[key] = most_common_value_type
        
        return common_structure
    
    elif most_common_type == 'list':
        # For nested lists, extract common structure recursively
        # Flatten and analyze all items from all lists
        all_nested_items = []
        for item in most_common_items:
            all_nested_items.extend(item)
        
        if len(all_nested_items) > 0:
            return [extract_common_list_structure(all_nested_items)]
        else:
            return []
    
    else:
        # For primitives, return the type name
        return most_common_type


def deep_compare_json(obj1: Any, obj2: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    Deeply compare two JSON objects by structure (schema) and return list of differences.
    Compares field names, types, and nested structures while ignoring example values.
    
    Args:
        obj1: First object to compare
        obj2: Second object to compare
        path: Current path in the object (for nested differences)
        
    Returns:
        List of differences with type, path, and values
    """
    differences = []
    
    # Type mismatch
    if type(obj1) != type(obj2):
        differences.append({
            'type': 'type_mismatch',
            'path': path or 'root',
            'legacy': type(obj1).__name__,
            'nextgen': type(obj2).__name__,
            'legacy_value': obj1,
            'nextgen_value': obj2
        })
        return differences
    
    # Compare dictionaries
    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                differences.append({
                    'type': 'added',
                    'path': new_path,
                    'nextgen_value': obj2[key]
                })
            elif key not in obj2:
                differences.append({
                    'type': 'removed',
                    'path': new_path,
                    'legacy_value': obj1[key]
                })
            else:
                # Recursively compare nested structures
                differences.extend(deep_compare_json(obj1[key], obj2[key], new_path))
    
    # Compare lists - ignore length, compare item structure only
    elif isinstance(obj1, list):
        # Ignore list length differences (length is variable in examples)
        # Extract common structure from all items, then compare
        if len(obj1) > 0 and len(obj2) > 0:
            # Both lists have items - extract common structure and compare
            item_path = f"{path}[*]" if path else "[*]"
            common_struct1 = extract_common_list_structure(obj1)
            common_struct2 = extract_common_list_structure(obj2)
            differences.extend(deep_compare_json(common_struct1, common_struct2, item_path))
        elif len(obj1) > 0 and len(obj2) == 0:
            # Legacy has items, nextgen is empty - report that array structure was removed
            item_path = f"{path}[*]" if path else "[*]"
            # Extract common structure to show what was removed
            struct = extract_common_list_structure(obj1)
            differences.append({
                'type': 'removed',
                'path': item_path,
                'legacy_value': struct
            })
        elif len(obj1) == 0 and len(obj2) > 0:
            # Legacy is empty, nextgen has items - report that array structure was added
            item_path = f"{path}[*]" if path else "[*]"
            # Extract common structure to show what was added
            struct = extract_common_list_structure(obj2)
            differences.append({
                'type': 'added',
                'path': item_path,
                'nextgen_value': struct
            })
        # If both are empty, no differences (same structure)
    
    # Compare primitive values - only report type mismatches, ignore value differences
    else:
        # Types already match (checked above), so no difference for structure comparison
        # Values are ignored for structure comparison
        pass
    
    return differences


def _strip_content_disposition_filename(value: str) -> str:
    """
    Remove filename-related parameters from a Content-Disposition header value.
    This lets us ignore differences where only the filename changes.
    """
    parts = [p.strip() for p in value.split(';')]
    filtered = []
    for part in parts:
        lower = part.lower()
        if lower.startswith('filename=') or lower.startswith('filename*='):
            continue
        if part:
            filtered.append(part)
    return '; '.join(filtered)


def _strip_multipart_boundary(value: str) -> str:
    """
    Remove boundary parameter from a Content-Type header value when it's multipart/form-data.
    This lets us ignore differences where only the boundary changes.
    """
    parts = [p.strip() for p in value.split(';')]
    filtered = []
    for part in parts:
        lower = part.lower()
        if lower.startswith('boundary='):
            continue
        if part:
            filtered.append(part)
    return '; '.join(filtered)


def compare_headers(
    headers1: Dict[str, str],
    headers2: Dict[str, str],
    ignore_content_disposition_filename: bool = False,
) -> Dict[str, Any]:
    """Compare two header dictionaries."""
    all_keys = set(headers1.keys()) | set(headers2.keys())
    
    added = {k: headers2[k] for k in all_keys if k not in headers1}
    removed = {k: headers1[k] for k in all_keys if k not in headers2}
    modified = {}
    
    for key in all_keys:
        if key in headers1 and key in headers2:
            if headers1[key] != headers2[key]:
                # Ignore Content-Disposition filename differences if requested
                if ignore_content_disposition_filename and key.lower() == 'content-disposition':
                    normalized1 = _strip_content_disposition_filename(headers1[key])
                    normalized2 = _strip_content_disposition_filename(headers2[key])
                    if normalized1 == normalized2:
                        continue
                # Ignore Content-Type boundary differences for multipart/form-data
                if key.lower() == 'content-type':
                    value1_lower = headers1[key].lower()
                    value2_lower = headers2[key].lower()
                    if 'multipart/form-data' in value1_lower and 'multipart/form-data' in value2_lower:
                        normalized1 = _strip_multipart_boundary(headers1[key])
                        normalized2 = _strip_multipart_boundary(headers2[key])
                        if normalized1 == normalized2:
                            continue
                modified[key] = {
                    'legacy': headers1[key],
                    'nextgen': headers2[key]
                }
    
    return {
        'added': added,
        'removed': removed,
        'modified': modified,
        'identical': len(added) == 0 and len(removed) == 0 and len(modified) == 0
    }


def compare_request_structures(legacy_entry: Dict[str, Any], nextgen_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Compare request structures between legacy and nextgen."""
    legacy_req = legacy_entry['request']
    nextgen_req = nextgen_entry['request']
    
    # Compare headers
    header_diff = compare_headers(legacy_req['headers'], nextgen_req['headers'])
    
    # Compare body
    body_diff = None
    if legacy_req['body'] or nextgen_req['body']:
        body_diff = deep_compare_json(legacy_req['body'], nextgen_req['body'])
    
    return {
        'method_identical': legacy_entry['method'] == nextgen_entry['method'],
        'headers': header_diff,
        'body': body_diff
    }


def compare_response_structures(legacy_entry: Dict[str, Any], nextgen_entry: Dict[str, Any]) -> Dict[str, Any]:
    """Compare response structures between legacy and nextgen."""
    legacy_resp = legacy_entry['response']
    nextgen_resp = nextgen_entry['response']
    
    # Compare status codes
    status_diff = {
        'legacy': legacy_resp['status'],
        'nextgen': nextgen_resp['status'],
        'identical': legacy_resp['status'] == nextgen_resp['status']
    }
    
    # Compare headers (ignore filename changes in Content-Disposition)
    header_diff = compare_headers(
        legacy_resp['headers'],
        nextgen_resp['headers'],
        ignore_content_disposition_filename=True,
    )
    
    # Compare body
    body_diff = None
    if legacy_resp['body'] or nextgen_resp['body']:
        body_diff = deep_compare_json(legacy_resp['body'], nextgen_resp['body'])
    
    return {
        'status': status_diff,
        'headers': header_diff,
        'body': body_diff
    }


def compare_apis(legacy_file: str, nextgen_file: str) -> Dict[str, Any]:
    """
    Compare APIs between legacy and nextgen HAR files using name-based matching.
    
    Args:
        legacy_file: Path to legacy HAR file
        nextgen_file: Path to nextgen HAR file
        
    Returns:
        Dictionary containing comparison results
    """
    # Parse HAR files (always require name field)
    legacy_entries = parse_har_file(legacy_file, require_name=True)
    nextgen_entries = parse_har_file(nextgen_file, require_name=True)
    
    # Group by name
    legacy_grouped = group_apis_by_name(legacy_entries)
    nextgen_grouped = group_apis_by_name(nextgen_entries)
    
    all_keys = set(legacy_grouped.keys()) | set(nextgen_grouped.keys())
    
    # Categorize keys
    common_keys = set(legacy_grouped.keys()) & set(nextgen_grouped.keys())
    legacy_only = set(legacy_grouped.keys()) - set(nextgen_grouped.keys())
    nextgen_only = set(nextgen_grouped.keys()) - set(legacy_grouped.keys())
    
    # Compare common keys
    key_comparisons = {}
    for key in common_keys:
        legacy_entry = legacy_grouped[key][0]  # Use first occurrence
        nextgen_entry = nextgen_grouped[key][0]  # Use first occurrence
        
        request_diff = compare_request_structures(legacy_entry, nextgen_entry)
        response_diff = compare_response_structures(legacy_entry, nextgen_entry)
        
        key_comparisons[key] = {
            'request': request_diff,
            'response': response_diff,
            'legacy_url': legacy_entry['original_url'],
            'nextgen_url': nextgen_entry['original_url']
        }
    
    # Collect legacy-only keys
    legacy_only_details = {}
    for key in legacy_only:
        entry = legacy_grouped[key][0]
        legacy_only_details[key] = {
            'url': entry['original_url'],
            'method': entry['method'],
            'path': entry['normalized_path']
        }
    
    # Collect nextgen-only keys
    nextgen_only_details = {}
    for key in nextgen_only:
        entry = nextgen_grouped[key][0]
        nextgen_only_details[key] = {
            'url': entry['original_url'],
            'method': entry['method'],
            'path': entry['normalized_path']
        }
    
    return {
        'summary': {
            'total_legacy_apis': len(legacy_grouped),
            'total_nextgen_apis': len(nextgen_grouped),
            'common_apis': len(common_keys),
            'legacy_only': len(legacy_only),
            'nextgen_only': len(nextgen_only)
        },
        'common_endpoints': key_comparisons,
        'legacy_only': legacy_only_details,
        'nextgen_only': nextgen_only_details
    }
