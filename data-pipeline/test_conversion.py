import re
import json
import ast

# Read the file
with open('/Users/tbardale/github/shadcn-ui/apps/v4/registry/registry-ui.ts', 'r') as f:
    content = f.read()

# Extract array content
pattern = r'export\s+(?:const|let|var)\s+(\w+)\s*:\s*Registry\["items"\]\s*=\s*(\[[\s\S]*?\])\s*$'
match = re.search(pattern, content, re.MULTILINE)
array_content = match.group(2)

print("Original array content (first 1000 chars):")
print(array_content[:1000])
print("\n" + "="*50 + "\n")

# Convert JavaScript to JSON
def js_to_json(js_content):
    content = js_content.replace('true', 'True').replace('false', 'False').replace('null', 'None')

    # Quote unquoted keys
    content = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', content)

    # Handle trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)

    print("After conversion (first 1000 chars):")
    print(content[:1000])
    print("\n" + "="*50 + "\n")

    try:
        result = ast.literal_eval(content)
        print("AST parsing successful!")
        return result
    except Exception as e:
        print(f"AST parsing failed: {e}")

        # Try JSON
        try:
            content_json = content.replace("'", '"')
            result = json.loads(content_json)
            print("JSON parsing successful!")
            return result
        except json.JSONDecodeError as je:
            print(f"JSON parsing failed: {je}")

            # Show error location
            lines = content_json.split('\n')
            for i, line in enumerate(lines):
                if '}' in line and '{' in line and '},' not in line:
                    print(f"Potential issue at line {i+1}: {line}")
                    break

            return None

result = js_to_json(array_content)
if result:
    print(f"\nSuccess! Parsed {len(result)} items")
    print("First item:", result[0])
else:
    print("\nFailed to parse")