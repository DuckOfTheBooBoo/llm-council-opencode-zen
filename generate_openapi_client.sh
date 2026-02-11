#!/bin/bash
# Script to generate OpenAPI Python client from OpenCode serve

set -e

OPENCODE_SERVER_URL="${OPENCODE_SERVER_URL:-http://127.0.0.1:4096}"
SPEC_FILE="openapi_spec.json"
OUTPUT_DIR="opencode_client"

echo "Fetching OpenAPI spec from ${OPENCODE_SERVER_URL}/doc..."

# Fetch the /doc page which contains the OpenAPI spec
curl -s "${OPENCODE_SERVER_URL}/doc" > doc.html || {
    echo "Error: Could not fetch OpenAPI spec from ${OPENCODE_SERVER_URL}/doc"
    echo "Make sure 'opencode serve' is running"
    exit 1
}

# Extract JSON from the HTML page
# The OpenAPI spec is typically embedded in the HTML as a script tag or data attribute
# We'll look for common patterns
if grep -q '"openapi"' doc.html; then
    # Try to extract JSON directly
    grep -oP '(?<=<script[^>]*>).*"openapi".*(?=</script>)' doc.html | head -1 > "${SPEC_FILE}" 2>/dev/null || {
        # Alternative: look for inline JSON in various formats
        python3 -c "
import re, json, sys
with open('doc.html', 'r') as f:
    content = f.read()
# Try to find JSON object with 'openapi' key
match = re.search(r'\{[^\{]*\"openapi\"[^\}]*\}', content, re.DOTALL)
if match:
    # This is a simple extraction, may need more sophisticated parsing
    json_str = match.group(0)
    # Try to extract full JSON
    depth = 0
    for i, c in enumerate(json_str):
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        if depth == 0:
            json_str = json_str[:i+1]
            break
    try:
        data = json.loads(json_str)
        with open('${SPEC_FILE}', 'w') as out:
            json.dump(data, out, indent=2)
        sys.exit(0)
    except:
        pass
sys.exit(1)
" || {
            echo "Error: Could not extract OpenAPI spec from HTML"
            echo "Please manually save the spec from ${OPENCODE_URL}/doc to ${SPEC_FILE}"
            exit 1
        }
    }
else
    echo "Error: OpenAPI spec not found in the HTML response"
    echo "Please manually save the spec from ${OPENCODE_SERVER_URL}/doc to ${SPEC_FILE}"
    exit 1
fi

echo "OpenAPI spec saved to ${SPEC_FILE}"

# Generate Python client using Docker
echo "Generating Python client..."
docker run --rm \
    -v "${PWD}:/local" \
    openapitools/openapi-generator-cli:latest generate \
    -i /local/${SPEC_FILE} \
    -g python \
    -o /local/${OUTPUT_DIR} \
    --additional-properties=packageName=opencode_client,projectName=opencode-client

echo "Python client generated in ${OUTPUT_DIR}/"
echo ""
echo "To install the client locally:"
echo "  cd ${OUTPUT_DIR}"
echo "  pip install -e ."

# Cleanup
rm -f doc.html
