"""HAR file parser for extracting API requests and responses."""

import json
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Optional


# Headers to ignore (infrastructure headers that don't affect API behavior)
IRRELEVANT_HEADERS = {
    'cache-control', 'date', 'server', 'alt-svc', 'nel', 'report-to',
    'server-timing', 'priority', 'content-encoding', 'transfer-encoding',
    'connection', 'keep-alive', 'cf-cache-status', 'cf-ray', 'cf-request-id',
    'cf-visitor', 'expect-ct', 'x-powered-by', 'x-content-type-options',
    'x-frame-options', 'x-xss-protection', 'strict-transport-security',
    'referrer-policy', 'via', 'x-request-id', 'x-runtime', 'x-ratelimit-*',
    'age', 'expires', 'last-modified', 'etag', 'vary', 'pragma',
    'accept-encoding', 'accept-language', 'user-agent', 'sec-ch-ua',
    'sec-ch-ua-mobile', 'sec-ch-ua-platform', 'sec-fetch-dest', 
    'sec-fetch-mode', 'sec-fetch-site', 'origin', 'referer',
    # HTTP/3 pseudo-headers
    ':scheme', ':path', ':method', ':authority', ':status',
    # HTTP/2 pseudo-headers
    'host',  # Host header is redundant when we have :authority or URL
    'if-none-match', 'access-token', 'cookie', 'set-cookie', 'content-length',
}

# Static asset extensions to filter out
STATIC_ASSET_EXTENSIONS = {
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.map', '.json', '.xml',
    '.pdf', '.zip', '.tar', '.gz'
}


def is_static_asset(url: str) -> bool:
    """Check if URL points to a static asset."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    return any(path.endswith(ext) for ext in STATIC_ASSET_EXTENSIONS)


def is_api_request(url: str) -> bool:
    """Check if URL is an API request (not a static asset)."""
    return not is_static_asset(url)


def normalize_url(url: str) -> str:
    """Normalize URL by removing hostname and query parameters."""
    parsed = urlparse(url)
    # Return just the path
    return parsed.path


def filter_headers(headers: List[Dict[str, str]]) -> Dict[str, str]:
    """Filter out irrelevant headers and return as dictionary."""
    filtered = {}
    for header in headers:
        name = header.get('name', '').lower()
        # Check if header should be ignored
        if any(name.startswith(irrelevant.replace('*', '')) for irrelevant in IRRELEVANT_HEADERS):
            continue
        # Also check exact matches
        if name in IRRELEVANT_HEADERS:
            continue
        filtered[name] = header.get('value', '')
    return filtered


def extract_request_body(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract and parse request body if present."""
    request = entry.get('request', {})
    post_data = request.get('postData')
    if not post_data:
        return None
    
    mime_type = post_data.get('mimeType', '')
    text = post_data.get('text', '')
    
    if not text:
        return None
    
    # Try to parse JSON
    if 'json' in mime_type.lower() and text.strip():
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {'_raw': text}
    
    return {'_raw': text, '_mime_type': mime_type}


def extract_response_body(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract and parse response body if present."""
    response = entry.get('response', {})
    content = response.get('content', {})
    
    if not content:
        return None
    
    mime_type = content.get('mimeType', '')
    text = content.get('text', '')
    
    if not text:
        return None
    
    # Try to parse JSON
    if 'json' in mime_type.lower() and text.strip():
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return {'_raw': text}
    
    return {'_raw': text, '_mime_type': mime_type}


def parse_har_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse HAR file and extract API requests/responses.
    
    Args:
        file_path: Path to HAR file
        
    Returns:
        List of API entries with normalized data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    api_entries = []
    
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url', '')
        
        # Skip static assets
        if not is_api_request(url):
            continue
        
        # Normalize URL
        normalized_path = normalize_url(url)
        
        # Extract request details
        method = request.get('method', '')
        request_headers = filter_headers(request.get('headers', []))
        request_body = extract_request_body(entry)
        
        # Extract response details
        response = entry.get('response', {})
        status_code = response.get('status', 0)
        response_headers = filter_headers(response.get('headers', []))
        response_body = extract_response_body(entry)
        
        api_entry = {
            'original_url': url,
            'normalized_path': normalized_path,
            'method': method,
            'request': {
                'headers': request_headers,
                'body': request_body
            },
            'response': {
                'status': status_code,
                'headers': response_headers,
                'body': response_body
            }
        }
        
        api_entries.append(api_entry)
    
    return api_entries


def group_apis_by_endpoint(api_entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group API entries by normalized endpoint path and HTTP method.
    
    Args:
        api_entries: List of parsed API entries
        
    Returns:
        Dictionary mapping "METHOD /path" to list of entries
    """
    grouped = {}
    for entry in api_entries:
        key = f"{entry['method']} {entry['normalized_path']}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(entry)
    return grouped
