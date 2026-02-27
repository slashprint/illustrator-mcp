import sys
sys.path.insert(0, 'C:/Users/internet/Desktop/mcp/illustrator-mcp/illustrator')

# Test imports
from extendscript_library import list_available_examples, get_all_examples
from design_guide import get_all_palettes, get_design_rules

print('=== ExtendScript Examples ===')
examples = list_available_examples()
for cat, items in examples.items():
    print(f'{cat}: {len(items)} examples')

print()
print('=== Color Palettes ===')
palettes = get_all_palettes()
for name, pal in palettes.items():
    print(f'{name}: {pal["description"]}')

print()
print('=== Design Rules ===')
rules = get_design_rules()
print(f"Do's: {len(rules['do'])} items")
print(f"Don'ts: {len(rules['dont'])} items")

print()
print('All modules loaded successfully!')
