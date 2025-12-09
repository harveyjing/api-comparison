#!/usr/bin/env python3
"""
Request Collection Script

Parses Chrome DevTools fetch files, makes API requests, and persists
request/response data to JSON files for later comparison.
"""

import json
import sys
import argparse
from urllib.parse import urlparse, urlencode
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import asdict

# Import from compare_apis
from compare_apis import FetchParser, APIRequest, APIComparator

# Optional import for making requests
try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def make_request(req: APIRequest, timeout: int = 10) -> Optional[Dict]:
    """Make an HTTP request and return response."""
    if not HAS_REQUESTS:
        return {
            'error': 'requests library not installed. Install with: pip install requests'
        }
    
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
        
        # Check if URL uses HTTPS to disable SSL verification
        parsed_url = urlparse(url)
        verify_ssl = False if parsed_url.scheme.lower() == 'https' else True
        
        # Prepare headers (filter out browser-specific headers)
        headers = {}
        skip_headers = {'sec-fetch-', 'sec-ch-ua', 'referrer', 'priority'}
        for key, value in req.headers.items():
            if not any(key.lower().startswith(skip) for skip in skip_headers):
                headers[key] = value
        
        # Make request
        if req.method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
        elif req.method.upper() == 'POST':
            data = req.body if req.body else None
            response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=verify_ssl)
        elif req.method.upper() == 'PUT':
            data = req.body if req.body else None
            response = requests.put(url, headers=headers, data=data, timeout=timeout, verify=verify_ssl)
        elif req.method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout, verify=verify_ssl)
        elif req.method.upper() == 'PATCH':
            data = req.body if req.body else None
            response = requests.patch(url, headers=headers, data=data, timeout=timeout, verify=verify_ssl)
        else:
            return {
                'error': f'Unsupported HTTP method: {req.method}'
            }
        
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
        print(f'Request to {req.url} failed: {str(e)}', file=sys.stderr)
        return {
            'error': f'Request failed: {str(e)}'
        }
    except Exception as e:
        print(f'Unexpected error for request to {req.url}: {str(e)}', file=sys.stderr)
        return {
            'error': f'Unexpected error: {str(e)}'
        }


def extract_metadata(requests: List[APIRequest]) -> Dict:
    """Extract base URLs and auth tokens from requests."""
    metadata = {
        'base_url': None,
        'auth_token': None
    }
    
    # Extract base URLs (most common base URL)
    if requests:
        base_urls = {}
        for req in requests:
            parsed = urlparse(req.url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            base_urls[base] = base_urls.get(base, 0) + 1
        if base_urls:
            metadata['base_url'] = max(base_urls.items(), key=lambda x: x[1])[0]
        
        # Extract auth tokens (most common token)
        tokens = {}
        for req in requests:
            # Check various auth header names
            for header_name in ['access-token', 'authorization', 'Authorization']:
                if header_name in req.headers:
                    token = req.headers[header_name]
                    if token and token.strip():
                        tokens[token] = tokens.get(token, 0) + 1
                        break
        if tokens:
            metadata['auth_token'] = max(tokens.items(), key=lambda x: x[1])[0]
    
    return metadata


def collect_requests(fetch_file: Path, timeout: int = 10) -> Dict:
    """Parse fetch file, make requests, and return data structure."""
    # Parse fetch file
    fetch_parser = FetchParser()
    requests_list = fetch_parser.parse_file(fetch_file)
    
    # Make requests and collect responses
    for req in requests_list:
        response = make_request(req, timeout)
        req.response = response
    
    # Extract metadata
    metadata = extract_metadata(requests_list)
    
    # Convert to dict format for JSON serialization
    requests_data = []
    for req in requests_list:
        req_dict = asdict(req)
        # Convert query_params values from list to list (keep as is for JSON)
        requests_data.append(req_dict)
    
    return {
        'metadata': metadata,
        'requests': requests_data
    }


def main():
    parser = argparse.ArgumentParser(
        description='Collect API requests and responses from fetch files'
    )
    parser.add_argument(
        'fetch_file',
        type=Path,
        help='Path to fetch file to parse'
    )
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output JSON file to save requests and responses'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Check if requests is available
    if not HAS_REQUESTS:
        print("Error: This script requires the 'requests' library.", file=sys.stderr)
        print("Install it with: pip install requests", file=sys.stderr)
        sys.exit(1)
    
    # Collect requests
    try:
        data = collect_requests(args.fetch_file, timeout=args.timeout)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error collecting requests: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save to file
    output_json = json.dumps(data, indent=2, ensure_ascii=False)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(output_json)
    
    print(f"Collected {len(data['requests'])} requests and saved to {args.output}")


if __name__ == '__main__':
    main()

