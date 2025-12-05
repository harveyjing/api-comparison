# API Comparison Tool

A Python script to compare REST API calls between old and new service versions. The tool parses Chrome DevTools fetch files and identifies differences in API paths, query parameters, payloads, and optionally response bodies.

## Features

- Parses Chrome DevTools fetch format files
- Compares API requests between old and new service versions
- Identifies differences in:
  - **Path**: API endpoint paths
  - **Query Parameters**: URL query string parameters
  - **Payload**: Request body (with JSON structure comparison)
  - **Response Body**: Optional comparison by making actual API calls
- Generates structured JSON output with detailed comparison results

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Compare two fetch files:

```bash
python compare_apis.py materials/1/old.fetch materials/1/new.fetch
```

### Save Output to File

```bash
python compare_apis.py materials/1/old.fetch materials/1/new.fetch -o comparison.json
```

### Compare Response Bodies

To also compare response bodies by making actual API calls (requires valid authentication tokens):

```bash
python compare_apis.py materials/1/old.fetch materials/1/new.fetch --compare-responses -o comparison.json
```

**Note**: Response comparison requires:
- Valid authentication tokens in the fetch files
- Network access to the API endpoints
- The tokens may be expired, so this feature may not work for all requests

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "summary": {
    "total_old": 27,
    "total_new": 25,
    "matched": 17,
    "only_in_old": 4,
    "only_in_new": 4
  },
  "matched": [
    {
      "method": "GET",
      "path": "/api/endpoint",
      "old_url": "https://old-service.com/api/endpoint",
      "new_url": "https://new-service.com/api/endpoint",
      "has_differences": true,
      "differences": {
        "query_params": {
          "old": {},
          "new": {"server": "lenovo-01"},
          "added": {"server": "lenovo-01"},
          "removed": {},
          "changed": {}
        },
        "payload": {
          "old": {"key": "old_value"},
          "new": {"key": "new_value"},
          "json_diff": {
            "added": {},
            "removed": {},
            "changed": {
              "key": {
                "old": "old_value",
                "new": "new_value"
              }
            }
          }
        }
      }
    }
  ],
  "only_in_old": [...],
  "only_in_new": [...]
}
```

### Output Sections

- **summary**: Statistics about the comparison
- **matched**: Requests that exist in both old and new versions, with differences highlighted
- **only_in_old**: Requests that only exist in the old version
- **only_in_new**: Requests that only exist in the new version

## How It Works

1. **Parsing**: The script parses JavaScript `fetch()` calls from Chrome DevTools export format
2. **Matching**: Requests are matched by HTTP method and API path (ignoring base URL differences)
3. **Comparison**: For matched requests, the script compares:
   - URL paths
   - Query parameters (identifies added, removed, and changed parameters)
   - Request payloads (with structured JSON comparison)
   - Response bodies (if `--compare-responses` is enabled)
4. **Output**: Results are formatted as structured JSON

## Limitations

- Response body comparison requires making actual API calls with valid authentication
- Authentication tokens in fetch files may be expired
- Some requests may be environment-specific (different servers, users)
- The parser expects standard Chrome DevTools fetch format

## Converting Results to Markdown

After generating the JSON comparison results, you can convert them to a human-readable Markdown report:

```bash
python json_to_markdown.py results.json -o report.md
```

The Markdown report includes:
- Metadata (base URLs and auth tokens)
- Summary statistics
- Matched requests with detailed differences
- Requests only in old/new versions

## Examples

### Example 1: Basic Comparison

```bash
python compare_apis.py materials/1/old.fetch materials/1/new.fetch -o results.json
```

### Example 2: With Response Comparison

```bash
python compare_apis.py materials/1/old.fetch materials/1/new.fetch --compare-responses -o results.json
```

### Example 3: Generate Markdown Report

```bash
# First, generate JSON results
python compare_apis.py materials/1/old.fetch materials/1/new.fetch -o results.json

# Then convert to Markdown
python json_to_markdown.py results.json -o report.md
```

## Troubleshooting

### Parser Errors

If you see "Failed to parse fetch call" warnings, the fetch file format may not be standard. Ensure the file was exported directly from Chrome DevTools.

### Response Comparison Failures

If response comparison fails:
- Check that authentication tokens are valid
- Verify network connectivity to the API endpoints
- Some requests may fail due to expired tokens or missing authentication

## License

This tool is provided as-is for API comparison purposes.

