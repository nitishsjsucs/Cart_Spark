import json

with open('CartSpark_Market_Basket_Analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
print(f"Code cells: {sum(1 for c in nb['cells'] if c['cell_type']=='code')}")
print(f"Markdown cells: {sum(1 for c in nb['cells'] if c['cell_type']=='markdown')}")

empty_cells = []
for i, cell in enumerate(nb['cells']):
    source = cell.get('source', [])
    if not source or (isinstance(source, list) and len(source) == 0):
        empty_cells.append(i)
        print(f"\nCell {i} is EMPTY (type: {cell['cell_type']})")

if empty_cells:
    print(f"\n❌ Found {len(empty_cells)} empty cells at indices: {empty_cells}")
else:
    print(f"\n✅ All cells have content!")

# Check first few cells
print("\n" + "="*60)
print("First 3 cells preview:")
for i in range(min(3, len(nb['cells']))):
    cell = nb['cells'][i]
    source = cell.get('source', [])
    content = ''.join(source) if isinstance(source, list) else source
    print(f"\nCell {i} ({cell['cell_type']}):")
    print(content[:100] + "..." if len(content) > 100 else content)
