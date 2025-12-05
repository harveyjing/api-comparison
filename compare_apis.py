#!/usr/bin/env python3
"""
API Comparison Script

Compares REST API calls between old and new service versions.
Parses Chrome DevTools fetch files and shows differences in:
- Path
- Query parameters
- Payload (request body)
- Response body (optional, requires API calls)
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
    
    def __init__(self, compare_responses: bool = False, timeout: int = 10):
        self.compare_responses = compare_responses
        self.timeout = timeout
    
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
        
        # Compare payload
        old_body = old_req.body_json if old_req.body_json else old_req.body
        new_body = new_req.body_json if new_req.body_json else new_req.body
        
        if old_body != new_body:
            payload_diff = {
                'old': old_body,
                'new': new_body
            }
            
            # If both are JSON, also include structured diff
            if old_req.body_json and new_req.body_json:
                json_diff = self._compare_json(old_req.body_json, new_req.body_json)
                if json_diff['added'] or json_diff['removed'] or json_diff['changed']:
                    payload_diff['json_diff'] = json_diff
            
            differences['payload'] = payload_diff
        
        # Response body comparison (if enabled)
        if self.compare_responses:
            response_diff = self._compare_responses(old_req, new_req)
            if response_diff:
                differences['response'] = response_diff
        
        result = {
            'method': old_req.method,
            'path': old_req.path,
            'has_differences': len(differences) > 0
        }
        
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
        """Compare two JSON objects and return differences."""
        diff = {
            'added': {},
            'removed': {},
            'changed': {}
        }
        
        old_keys = set(old_json.keys()) if isinstance(old_json, dict) else set()
        new_keys = set(new_json.keys()) if isinstance(new_json, dict) else set()
        
        if isinstance(old_json, dict) and isinstance(new_json, dict):
            for key in new_keys - old_keys:
                diff['added'][key] = new_json[key]
            
            for key in old_keys - new_keys:
                diff['removed'][key] = old_json[key]
            
            for key in old_keys & new_keys:
                if old_json[key] != new_json[key]:
                    diff['changed'][key] = {
                        'old': old_json[key],
                        'new': new_json[key]
                    }
        
        return diff
    
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
        
        return result
    
    def _compare_responses(self, old_req: APIRequest, 
                          new_req: APIRequest) -> Optional[Dict]:
        """Compare response bodies by making API calls."""
        if not HAS_REQUESTS:
            return {
                'error': 'requests library not installed. Install with: pip install requests'
            }
        
        try:
            old_response = self._make_request(old_req)
            new_response = self._make_request(new_req)
            
            if old_response is None or new_response is None:
                return {
                    'error': 'Failed to fetch one or both responses',
                    'old_success': old_response is not None,
                    'new_success': new_response is not None
                }
            
            # Compare status codes
            status_diff = None
            if old_response.get('status_code') != new_response.get('status_code'):
                status_diff = {
                    'old': old_response.get('status_code'),
                    'new': new_response.get('status_code')
                }
            
            # Compare response bodies
            old_body = old_response.get('body')
            new_body = new_response.get('body')
            
            body_diff = None
            if old_body != new_body:
                # Try to parse as JSON for structured comparison
                old_json = None
                new_json = None
                
                try:
                    old_json = json.loads(old_body) if old_body else None
                except (json.JSONDecodeError, TypeError):
                    pass
                
                try:
                    new_json = json.loads(new_body) if new_body else None
                except (json.JSONDecodeError, TypeError):
                    pass
                
                if old_json is not None and new_json is not None:
                    # Both are JSON, do structured comparison
                    json_diff = self._compare_json(old_json, new_json)
                    body_diff = {
                        'old': old_json,
                        'new': new_json,
                        'json_diff': json_diff
                    }
                else:
                    # Text comparison
                    body_diff = {
                        'old': old_body,
                        'new': new_body
                    }
            
            if status_diff or body_diff:
                return {
                    'status_code': status_diff,
                    'body': body_diff
                }
            
            return None  # No differences
            
        except Exception as e:
            return {
                'error': f'Error comparing responses: {str(e)}'
            }
    
    def _make_request(self, req: APIRequest) -> Optional[Dict]:
        """Make an HTTP request and return response."""
        try:
            # Build URL with query parameters
            url = req.url
            if req.query_params:
                # Reconstruct URL with query params
                parsed = urlparse(url)
                query_string = urlencode(
                    {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                     for k, v in req.query_params.items()},
                    doseq=True
                )
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"
            
            # Prepare headers (filter out browser-specific headers)
            headers = {}
            skip_headers = {'sec-fetch-', 'sec-ch-ua', 'referrer', 'priority'}
            for key, value in req.headers.items():
                if not any(key.lower().startswith(skip) for skip in skip_headers):
                    headers[key] = value
            
            # Make request
            if req.method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout)
            elif req.method.upper() == 'POST':
                data = req.body if req.body else None
                response = requests.post(url, headers=headers, data=data, timeout=self.timeout)
            elif req.method.upper() == 'PUT':
                data = req.body if req.body else None
                response = requests.put(url, headers=headers, data=data, timeout=self.timeout)
            elif req.method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=self.timeout)
            elif req.method.upper() == 'PATCH':
                data = req.body if req.body else None
                response = requests.patch(url, headers=headers, data=data, timeout=self.timeout)
            else:
                return None
            
            # Get response body
            try:
                body = response.json()
                body_str = json.dumps(body, indent=2)
            except (ValueError, json.JSONDecodeError):
                body = response.text
                body_str = body
            
            return {
                'status_code': response.status_code,
                'body': body_str,
                'body_json': body if isinstance(body, dict) else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}'
            }


def main():
    parser = argparse.ArgumentParser(
        description='Compare REST API calls between old and new service versions'
    )
    parser.add_argument(
        'old_file',
        type=Path,
        help='Path to old service fetch file'
    )
    parser.add_argument(
        'new_file',
        type=Path,
        help='Path to new service fetch file'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output JSON file (default: stdout)'
    )
    parser.add_argument(
        '--compare-responses',
        action='store_true',
        help='Compare response bodies (requires making API calls)'
    )
    
    args = parser.parse_args()
    
    # Check if requests is available when response comparison is requested
    if args.compare_responses and not HAS_REQUESTS:
        print("Error: --compare-responses requires the 'requests' library.", file=sys.stderr)
        print("Install it with: pip install requests", file=sys.stderr)
        sys.exit(1)
    
    # Parse files
    fetch_parser = FetchParser()
    
    try:
        old_requests = fetch_parser.parse_file(args.old_file)
        new_requests = fetch_parser.parse_file(args.new_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing files: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compare
    comparator = APIComparator(compare_responses=args.compare_responses)
    results = comparator.compare(old_requests, new_requests)
    
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

