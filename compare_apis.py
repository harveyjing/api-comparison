#!/usr/bin/env python3
"""
API Comparison Script

Compares REST API calls between old and new service versions.
Loads saved request/response data from JSON files and shows differences in:
- Path
- Query parameters
- Payload (request body)
- Response body
"""

import re
import json
import sys
import argparse
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Optional import for response comparison
try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@dataclass
class APIRequest:
    """Represents a parsed API request."""
    url: str
    method: str
    path: str
    query_params: Dict[str, List[str]]
    headers: Dict[str, str]
    body: Optional[str]
    body_json: Optional[Dict] = None
    response: Optional[Dict] = None
    
    def __post_init__(self):
        """Parse body as JSON if possible."""
        if self.body and self.body != "null":
            try:
                self.body_json = json.loads(self.body)
            except (json.JSONDecodeError, TypeError):
                pass
    
    def get_normalized_path(self) -> str:
        """Get path without base URL for matching."""
        return self.path
    
    def get_match_key(self) -> str:
        """Get a key for matching requests between old and new."""
        # Use method + path for matching
        return f"{self.method}:{self.path}"


class FetchParser:
    """Parser for Chrome DevTools fetch format."""
    
    def __init__(self):
        # Pattern to match fetch() calls
        # Matches: fetch("url", { ... });
        self.fetch_pattern = re.compile(
            r'fetch\s*\(\s*"([^"]+)"\s*,\s*(\{[^}]*\})\s*\)\s*;',
            re.DOTALL
        )
    
    def parse_file(self, file_path: Path) -> List[APIRequest]:
        """Parse a fetch file and return list of APIRequest objects."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        requests = []
        # Split by fetch calls (more reliable than regex for nested objects)
        fetch_calls = self._extract_fetch_calls(content)
        
        for url, options_json in fetch_calls:
            try:
                # Parse the options object
                options = json.loads(options_json)
                
                # Extract components
                method = options.get('method', 'GET')
                headers = options.get('headers', {})
                body = options.get('body')
                if body == "null":
                    body = None
                
                # Parse URL
                parsed_url = urlparse(url)
                path = parsed_url.path
                query_params = parse_qs(parsed_url.query, keep_blank_values=True)
                
                request = APIRequest(
                    url=url,
                    method=method,
                    path=path,
                    query_params=query_params,
                    headers=headers,
                    body=body
                )
                requests.append(request)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Failed to parse fetch call: {e}", file=sys.stderr)
                continue
        
        return requests
    
    def _extract_fetch_calls(self, content: str) -> List[Tuple[str, str]]:
        """Extract fetch calls from content, handling nested JSON objects."""
        calls = []
        i = 0
        
        while i < len(content):
            # Find next fetch(
            fetch_start = content.find('fetch(', i)
            if fetch_start == -1:
                break
            
            # Find the opening quote for URL
            url_start = content.find('"', fetch_start)
            if url_start == -1:
                i = fetch_start + 1
                continue
            
            # Find the closing quote for URL
            url_end = content.find('"', url_start + 1)
            if url_end == -1:
                i = url_start + 1
                continue
            
            url = content[url_start + 1:url_end]
            
            # Find the opening brace for options
            brace_start = content.find('{', url_end)
            if brace_start == -1:
                i = url_end + 1
                continue
            
            # Find matching closing brace
            brace_count = 0
            brace_end = brace_start
            in_string = False
            escape_next = False
            
            for j in range(brace_start, len(content)):
                char = content[j]
                
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"':
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            brace_end = j
                            break
            
            if brace_count == 0:
                options_json = content[brace_start:brace_end + 1]
                calls.append((url, options_json))
                i = brace_end + 1
            else:
                i = brace_start + 1
        
        return calls


class APIComparator:
    """Compares API requests between old and new versions."""
    
    def __init__(self):
        pass
    
    def compare(self, old_requests: List[APIRequest], 
                new_requests: List[APIRequest]) -> Dict:
        """Compare old and new requests and return comparison results."""
        # Extract metadata (base URLs and auth tokens)
        metadata = self._extract_metadata(old_requests, new_requests)
        
        # Build index by match key
        old_index = {req.get_match_key(): req for req in old_requests}
        new_index = {req.get_match_key(): req for req in new_requests}
        
        # Find matches and differences
        matched = []
        only_in_old = []
        only_in_new = []
        
        all_keys = set(old_index.keys()) | set(new_index.keys())
        
        for key in all_keys:
            old_req = old_index.get(key)
            new_req = new_index.get(key)
            
            if old_req and new_req:
                diff = self._compare_requests(old_req, new_req, metadata)
                matched.append(diff)
            elif old_req:
                only_in_old.append(self._request_to_dict(old_req, metadata))
            elif new_req:
                only_in_new.append(self._request_to_dict(new_req, metadata))
        
        return {
            'metadata': metadata,
            'summary': {
                'total_old': len(old_requests),
                'total_new': len(new_requests),
                'matched': len(matched),
                'only_in_old': len(only_in_old),
                'only_in_new': len(only_in_new)
            },
            'matched': matched,
            'only_in_old': only_in_old,
            'only_in_new': only_in_new
        }
    
    def _extract_metadata(self, old_requests: List[APIRequest], 
                         new_requests: List[APIRequest]) -> Dict:
        """Extract base URLs and auth tokens from requests."""
        metadata = {
            'old_base_url': None,
            'new_base_url': None,
            'old_auth_token': None,
            'new_auth_token': None
        }
        
        # Extract base URLs (most common base URL)
        if old_requests:
            base_urls = {}
            for req in old_requests:
                parsed = urlparse(req.url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                base_urls[base] = base_urls.get(base, 0) + 1
            if base_urls:
                metadata['old_base_url'] = max(base_urls.items(), key=lambda x: x[1])[0]
        
        if new_requests:
            base_urls = {}
            for req in new_requests:
                parsed = urlparse(req.url)
                base = f"{parsed.scheme}://{parsed.netloc}"
                base_urls[base] = base_urls.get(base, 0) + 1
            if base_urls:
                metadata['new_base_url'] = max(base_urls.items(), key=lambda x: x[1])[0]
        
        # Extract auth tokens (most common token)
        if old_requests:
            tokens = {}
            for req in old_requests:
                # Check various auth header names
                for header_name in ['access-token', 'authorization', 'Authorization']:
                    if header_name in req.headers:
                        token = req.headers[header_name]
                        if token and token.strip():
                            tokens[token] = tokens.get(token, 0) + 1
                            break
            if tokens:
                metadata['old_auth_token'] = max(tokens.items(), key=lambda x: x[1])[0]
        
        if new_requests:
            tokens = {}
            for req in new_requests:
                for header_name in ['access-token', 'authorization', 'Authorization']:
                    if header_name in req.headers:
                        token = req.headers[header_name]
                        if token and token.strip():
                            tokens[token] = tokens.get(token, 0) + 1
                            break
            if tokens:
                metadata['new_auth_token'] = max(tokens.items(), key=lambda x: x[1])[0]
        
        return metadata
    
    def _compare_requests(self, old_req: APIRequest, 
                         new_req: APIRequest, metadata: Dict) -> Dict:
        """Compare two matched requests."""
        differences = {}
        
        # Compare path
        if old_req.path != new_req.path:
            differences['path'] = {
                'old': old_req.path,
                'new': new_req.path
            }
        
        # Compare query parameters
        old_params = self._normalize_params(old_req.query_params)
        new_params = self._normalize_params(new_req.query_params)
        if old_params != new_params:
            # Include full old/new for table display, plus diff details
            param_diff = {
                'old': old_params,
                'new': new_params
            }
            added = {k: v for k, v in new_params.items() if k not in old_params}
            removed = {k: v for k, v in old_params.items() if k not in new_params}
            changed = {
                k: {'old': old_params[k], 'new': new_params[k]}
                for k in old_params.keys() & new_params.keys()
                if old_params[k] != new_params[k]
            }
            
            if added:
                param_diff['added'] = added
            if removed:
                param_diff['removed'] = removed
            if changed:
                param_diff['changed'] = changed
            
            differences['query_params'] = param_diff
        
        # Compare payload (structure only, not values)
        old_body = old_req.body_json if old_req.body_json else old_req.body
        new_body = new_req.body_json if new_req.body_json else new_req.body
        
        # If both are JSON, compare structure only
        if old_req.body_json and new_req.body_json:
            json_diff = self._compare_json(old_req.body_json, new_req.body_json)
            if json_diff['added'] or json_diff['removed'] or json_diff['changed']:
                payload_diff = {
                    'old': old_body,
                    'new': new_body,
                    'json_diff': json_diff
                }
                differences['payload'] = payload_diff
        elif old_body != new_body:
            # For non-JSON payloads, still compare values
            payload_diff = {
                'old': old_body,
                'new': new_body
            }
            differences['payload'] = payload_diff
        
        # Response body comparison (from saved data)
        response_data = None
        if old_req.response is not None or new_req.response is not None:
            response_data = self._compare_saved_responses(old_req, new_req)
            if response_data and 'error' not in response_data:
                # Check if there are actual differences in the response
                has_response_diff = False
                if 'status_code' in response_data:
                    status_code = response_data['status_code']
                    if isinstance(status_code, dict) and status_code.get('old') != status_code.get('new'):
                        has_response_diff = True
                if 'body' in response_data:
                    body = response_data['body']
                    if isinstance(body, dict):
                        if 'json_diff' in body:
                            has_response_diff = True
                        elif body.get('old') != body.get('new'):
                            has_response_diff = True
                
                if has_response_diff:
                    differences['response'] = response_data
        
        result = {
            'method': old_req.method,
            'path': old_req.path,
            'has_differences': len(differences) > 0
        }
        
        # Always include response data if available, even if no differences
        if response_data:
            result['response'] = response_data
        
        if differences:
            result['differences'] = differences
        
        return result
    
    def _normalize_params(self, params: Dict[str, List[str]]) -> Dict[str, str]:
        """Normalize query parameters for comparison."""
        normalized = {}
        for key, values in params.items():
            # Sort values for consistent comparison
            normalized[key] = sorted(values) if len(values) > 1 else values[0] if values else ''
        return normalized
    
    def _compare_json(self, old_json: Dict, new_json: Dict) -> Dict:
        """Compare two JSON objects and return differences (structure only, not values)."""
        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        old_keys = set(old_json.keys()) if isinstance(old_json, dict) else set()
        new_keys = set(new_json.keys()) if isinstance(new_json, dict) else set()
        
        if isinstance(old_json, dict) and isinstance(new_json, dict):
            for key in new_keys - old_keys:
                # Store structure info, not actual value
                diff['added'][key] = self._get_structure(new_json[key])
            
            for key in old_keys - new_keys:
                # Store structure info, not actual value
                diff['removed'][key] = self._get_structure(old_json[key])
            
            for key in old_keys & new_keys:
                old_val = old_json[key]
                new_val = new_json[key]
                
                # Compare structures, not values
                # If both are objects, always recursively compare their structure
                if isinstance(old_val, dict) and isinstance(new_val, dict):
                    nested_diff = self._compare_json(old_val, new_val)
                    if nested_diff['added'] or nested_diff['removed'] or nested_diff['changed']:
                        diff['changed'][key] = nested_diff
                elif isinstance(old_val, list) and isinstance(new_val, list):
                    # Compare list structures - check if items have different structures
                    old_item_types = [self._get_structure(item) for item in old_val]
                    new_item_types = [self._get_structure(item) for item in new_val]
                    if old_item_types != new_item_types:
                        diff['changed'][key] = {
                            'old_structure': old_item_types,
                            'new_structure': new_item_types
                        }
                elif self._has_structure_difference(old_val, new_val):
                    # Different types or structures
                    diff['changed'][key] = {
                        'old_type': self._get_structure(old_val),
                        'new_type': self._get_structure(new_val)
                    }
        
        return diff
    
    def _get_structure(self, value) -> str:
        """Get a string representation of the structure/type of a value."""
        if isinstance(value, dict):
            return f"object({', '.join(sorted(value.keys()))})"
        elif isinstance(value, list):
            if len(value) == 0:
                return "array[]"
            # Get structure of first item as representative
            first_item_structure = self._get_structure(value[0])
            return f"array[{first_item_structure}]"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif value is None:
            return "null"
        else:
            return type(value).__name__
    
    def _has_structure_difference(self, old_val, new_val) -> bool:
        """Check if two values have different structures (not values)."""
        # Different types
        if type(old_val) != type(new_val):
            return True
        
        # Both are dicts - compare keys only
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            return set(old_val.keys()) != set(new_val.keys())
        
        # Both are lists - compare item structures
        if isinstance(old_val, list) and isinstance(new_val, list):
            if len(old_val) != len(new_val):
                return True
            # Compare structures of items
            old_structures = [self._get_structure(item) for item in old_val]
            new_structures = [self._get_structure(item) for item in new_val]
            return old_structures != new_structures
        
        # For primitive types, structure is the same (we don't compare values)
        return False
    
    def _request_to_dict(self, req: APIRequest, metadata: Dict) -> Dict:
        """Convert APIRequest to dictionary (without base URL and auth token)."""
        result = {
            'method': req.method,
            'path': req.path
        }
        
        # Add query params if present
        params = self._normalize_params(req.query_params)
        if params:
            result['query_params'] = params
        
        # Add payload if present
        payload = req.body_json if req.body_json else req.body
        if payload:
            result['payload'] = payload
        
        # Add response data if present
        if req.response is not None:
            response_data = self._format_single_response(req.response)
            if response_data:
                result['response'] = response_data
        
        return result
    
    def _format_single_response(self, response: Dict) -> Optional[Dict]:
        """Format a single response (not a comparison) for inclusion in only_in_old/only_in_new."""
        # Handle errors in responses
        if 'error' in response:
            return {
                'error': response['error'],
                'success': False
            }
        
        result = {}
        
        # Always include status code if available
        if 'status_code' in response:
            result['status_code'] = response['status_code']
        
        # Always include response body if available
        if 'body' in response:
            body = response['body']
            # Try to parse as JSON if it's a string
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except (json.JSONDecodeError, TypeError):
                    pass
            result['body'] = body
        elif 'body_json' in response:
            result['body'] = response['body_json']
        
        return result if result else None
    
    def _compare_saved_responses(self, old_req: APIRequest, 
                                 new_req: APIRequest) -> Optional[Dict]:
        """Compare response bodies from saved response data."""
        old_response = old_req.response
        new_response = new_req.response
        
        # Handle errors in responses
        if old_response and 'error' in old_response:
            return {
                'error': f"Old request error: {old_response['error']}",
                'old_success': False,
                'new_success': new_response is not None and 'error' not in new_response
            }
        
        if new_response and 'error' in new_response:
            return {
                'error': f"New request error: {new_response['error']}",
                'old_success': old_response is not None and 'error' not in old_response,
                'new_success': False
            }
        
        if old_response is None and new_response is None:
            return None
        
        if old_response is None or new_response is None:
            return {
                'error': 'One or both responses are missing',
                'old_success': old_response is not None,
                'new_success': new_response is not None
            }
        
        # Always include status codes
        old_status = old_response.get('status_code')
        new_status = new_response.get('status_code')
        status_code = {
            'old': old_status,
            'new': new_status
        }
        
        # Always include response bodies
        old_body = old_response.get('body')
        new_body = new_response.get('body')
        
        # Try to parse as JSON for structured comparison
        old_json = None
        new_json = None
        
        # Use body_json if available, otherwise parse body string
        if old_response.get('body_json') is not None:
            old_json = old_response.get('body_json')
        elif old_body:
            try:
                old_json = json.loads(old_body) if old_body else None
            except (json.JSONDecodeError, TypeError):
                pass
        
        if new_response.get('body_json') is not None:
            new_json = new_response.get('body_json')
        elif new_body:
            try:
                new_json = json.loads(new_body) if new_body else None
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Always include body data
        if old_json is not None and new_json is not None:
            # Both are JSON, compare structure
            json_diff = self._compare_json(old_json, new_json)
            body = {
                'old': old_json,
                'new': new_json
            }
            # Only include json_diff if there are differences
            if json_diff['added'] or json_diff['removed'] or json_diff['changed']:
                body['json_diff'] = json_diff
        else:
            # Text comparison (non-JSON)
            body = {
                'old': old_body,
                'new': new_body
            }
        
        # Always return response data, even if there are no differences
        return {
            'status_code': status_code,
            'body': body
        }
    


def load_requests_from_file(file_path: Path) -> Tuple[List[APIRequest], Dict]:
    """Load APIRequest objects from saved JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.get('metadata', {})
    requests_data = data.get('requests', [])
    
    # Convert dicts back to APIRequest objects
    requests = []
    for req_dict in requests_data:
        # Convert query_params back to Dict[str, List[str]] format
        query_params = req_dict.get('query_params', {})
        if query_params:
            # Ensure values are lists
            normalized_query_params = {}
            for k, v in query_params.items():
                if isinstance(v, list):
                    normalized_query_params[k] = v
                else:
                    normalized_query_params[k] = [v] if v else ['']
            req_dict['query_params'] = normalized_query_params
        
        # Create APIRequest object
        req = APIRequest(
            url=req_dict.get('url', ''),
            method=req_dict.get('method', 'GET'),
            path=req_dict.get('path', ''),
            query_params=req_dict.get('query_params', {}),
            headers=req_dict.get('headers', {}),
            body=req_dict.get('body'),
            body_json=req_dict.get('body_json'),
            response=req_dict.get('response')
        )
        requests.append(req)
    
    return requests, metadata


def main():
    parser = argparse.ArgumentParser(
        description='Compare REST API calls between old and new service versions from saved data'
    )
    parser.add_argument(
        'old_file',
        type=Path,
        help='Path to old service saved requests JSON file'
    )
    parser.add_argument(
        'new_file',
        type=Path,
        help='Path to new service saved requests JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output JSON file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Load saved request files
    try:
        old_requests, old_metadata = load_requests_from_file(args.old_file)
        new_requests, new_metadata = load_requests_from_file(args.new_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Merge metadata
    metadata = {
        'old_base_url': old_metadata.get('base_url'),
        'new_base_url': new_metadata.get('base_url'),
        'old_auth_token': old_metadata.get('auth_token'),
        'new_auth_token': new_metadata.get('auth_token')
    }
    
    # Compare
    comparator = APIComparator()
    results = comparator.compare(old_requests, new_requests)
    
    # Override metadata with loaded metadata
    results['metadata'] = metadata
    
    # Output
    output_json = json.dumps(results, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Comparison results written to {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()

