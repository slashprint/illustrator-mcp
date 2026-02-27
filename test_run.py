import sys
sys.path.insert(0, 'C:/Users/internet/Desktop/mcp/illustrator-mcp/illustrator')
from server import run_illustrator_script

print("=== Test 1: Return number ===")
result = run_illustrator_script("app.textFonts.length;")
print(f"Result: {result[0].text}")

print("\n=== Test 2: Return string ===")
result = run_illustrator_script("app.name;")
print(f"Result: {result[0].text}")

print("\n=== Test 3: toJSON with utils ===")
result = run_illustrator_script('toJSON(["a", "b", "c"]);', include_utils=True)
print(f"Result: {result[0].text}")

print("\n=== Test 4: Font list (first 5) ===")
code = '''
var r = [];
for (var i = 0; i < Math.min(5, app.textFonts.length); i++) {
    r.push(app.textFonts[i].name);
}
toJSON(r);
'''
result = run_illustrator_script(code, include_utils=True)
print(f"Result: {result[0].text}")
