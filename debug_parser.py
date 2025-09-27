import re

# Read the file
with open('/Users/tbardale/github/shadcn-ui/apps/v4/registry/registry-ui.ts', 'r') as f:
    content = f.read()

# Test the pattern without semicolon
pattern = r'export\s+(?:const|let|var)\s+(\w+)\s*:\s*Registry\["items"\]\s*=\s*(\[[\s\S]*?\])\s*$'
match = re.search(pattern, content, re.MULTILINE)
print("Pattern match:", match is not None)

if match:
    print("Groups:", len(match.groups()))
    print("Group 1:", match.group(1))
    array_content = match.group(2)
    print("Group 2 length:", len(array_content))
    print("Group 2 first 500 chars:")
    print(array_content[:500])
    print("\n...")
    print("Group 2 last 100 chars:")
    print(array_content[-100:])

    # Try to clean and parse
    print("\nTrying to parse...")
    # Replace JavaScript-specific syntax with Python-compatible
    cleaned = array_content.replace('true', 'True').replace('false', 'False').replace('null', 'None')

    try:
        import ast
        parsed = ast.literal_eval(cleaned)
        print("Successfully parsed! Length:", len(parsed))
        print("First item keys:", list(parsed[0].keys()) if parsed else "Empty")
    except Exception as e:
        print("Parse error:", e)
        print("Trying position of error...")
else:
    print("No match found")