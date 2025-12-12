"""API comparison engine for comparing legacy and nextgen APIs."""

from typing import Dict, List, Any, Set, Tuple
from har_parser import group_apis_by_endpoint, parse_har_file
import json


def deep_compare_json(obj1: Any, obj2: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    Deeply compare two JSON objects and return list of differences.
    
    Args:
        obj1: First object to compare
        obj2: Second object to compare
        path: Current path in the object (for nested differences)
        
    Returns:
        List of differences with type, path, and values
    """
    differences = []
    
    # Both None or same value
    if obj1 == obj2:
        return differences
    
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
                differences.extend(deep_compare_json(obj1[key], obj2[key], new_path))
    
    # Compare lists
    elif isinstance(obj1, list):
        max_len = max(len(obj1), len(obj2))
        for i in range(max_len):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            if i >= len(obj1):
                differences.append({
                    'type': 'added',
                    'path': new_path,
                    'nextgen_value': obj2[i]
                })
            elif i >= len(obj2):
                differences.append({
                    'type': 'removed',
                    'path': new_path,
                    'legacy_value': obj1[i]
                })
            else:
                differences.extend(deep_compare_json(obj1[i], obj2[i], new_path))
    
    # Compare primitive values
    else:
        differences.append({
            'type': 'modified',
            'path': path or 'root',
            'legacy_value': obj1,
            'nextgen_value': obj2
        })
    
    return differences


def compare_headers(headers1: Dict[str, str], headers2: Dict[str, str]) -> Dict[str, Any]:
    """Compare two header dictionaries."""
    all_keys = set(headers1.keys()) | set(headers2.keys())
    
    added = {k: headers2[k] for k in all_keys if k not in headers1}
    removed = {k: headers1[k] for k in all_keys if k not in headers2}
    modified = {}
    
    for key in all_keys:
        if key in headers1 and key in headers2:
            if headers1[key] != headers2[key]:
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
    
    # Compare headers
    header_diff = compare_headers(legacy_resp['headers'], nextgen_resp['headers'])
    
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
    Compare APIs between legacy and nextgen HAR files.
    
    Args:
        legacy_file: Path to legacy HAR file
        nextgen_file: Path to nextgen HAR file
        
    Returns:
        Dictionary containing comparison results
    """
    # Parse HAR files
    legacy_entries = parse_har_file(legacy_file)
    nextgen_entries = parse_har_file(nextgen_file)
    
    # Group by endpoint
    legacy_grouped = group_apis_by_endpoint(legacy_entries)
    nextgen_grouped = group_apis_by_endpoint(nextgen_entries)
    
    all_endpoints = set(legacy_grouped.keys()) | set(nextgen_grouped.keys())
    
    # Categorize endpoints
    common_endpoints = set(legacy_grouped.keys()) & set(nextgen_grouped.keys())
    legacy_only = set(legacy_grouped.keys()) - set(nextgen_grouped.keys())
    nextgen_only = set(nextgen_grouped.keys()) - set(legacy_grouped.keys())
    
    # Compare common endpoints
    endpoint_comparisons = {}
    for endpoint in common_endpoints:
        legacy_entry = legacy_grouped[endpoint][0]  # Use first occurrence
        nextgen_entry = nextgen_grouped[endpoint][0]  # Use first occurrence
        
        request_diff = compare_request_structures(legacy_entry, nextgen_entry)
        response_diff = compare_response_structures(legacy_entry, nextgen_entry)
        
        endpoint_comparisons[endpoint] = {
            'request': request_diff,
            'response': response_diff,
            'legacy_url': legacy_entry['original_url'],
            'nextgen_url': nextgen_entry['original_url']
        }
    
    # Collect legacy-only endpoints
    legacy_only_details = {}
    for endpoint in legacy_only:
        entry = legacy_grouped[endpoint][0]
        legacy_only_details[endpoint] = {
            'url': entry['original_url'],
            'method': entry['method'],
            'path': entry['normalized_path']
        }
    
    # Collect nextgen-only endpoints
    nextgen_only_details = {}
    for endpoint in nextgen_only:
        entry = nextgen_grouped[endpoint][0]
        nextgen_only_details[endpoint] = {
            'url': entry['original_url'],
            'method': entry['method'],
            'path': entry['normalized_path']
        }
    
    return {
        'summary': {
            'total_legacy_apis': len(legacy_grouped),
            'total_nextgen_apis': len(nextgen_grouped),
            'common_apis': len(common_endpoints),
            'legacy_only': len(legacy_only),
            'nextgen_only': len(nextgen_only)
        },
        'common_endpoints': endpoint_comparisons,
        'legacy_only': legacy_only_details,
        'nextgen_only': nextgen_only_details
    }
