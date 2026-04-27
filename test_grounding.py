#!/usr/bin/env python3
"""
Test A & Test B – Verify grounded recommendations (no more repetitive 3 products).
"""

from engine import process_mumz_request
from tabulate import tabulate

print("\n" + "="*80)
print("GROUNDING TEST – Stroller vs Teething")
print("="*80 + "\n")

tests = [
    {
        "name": "Test A – Stroller Query",
        "input": "I need a lightweight stroller for travel.",
        "expected_category": "Travel",
        "expected_products": ["Travel System", "Diaper Bag", "Car Seat Stroller"],
        "forbidden_products": ["Breast Pump", "Bottle", "Monitor"]
    },
    {
        "name": "Test B – Teething Query",
        "input": "My baby's gums are hurting.",
        "expected_category": "Feeding/Toys (teething)",
        "expected_products": ["Bottle", "Pump", "Toys"],
        "forbidden_products": ["Stroller", "Car Seat"]
    }
]

results = []

for test in tests:
    result = process_mumz_request(test["input"])
    rec_names = [r['name'] for r in result.get('recommendations', [])]
    rec_names_lower = [n.lower() for n in rec_names]
    
    # Check if ANY expected product appears
    has_expected = any(
        any(exp.lower() in name for name in rec_names_lower)
        for exp in test["expected_products"]
    )
    
    # Check if ANY forbidden product appears
    has_forbidden = any(
        any(forb.lower() in name for name in rec_names_lower)
        for forb in test["forbidden_products"]
    )
    
    status = "PASS" if (has_expected and not has_forbidden) else "FAIL"
    
    results.append([
        test["name"],
        result.get('detected_milestone', 'N/A'),
        ", ".join(rec_names) if rec_names else "(none)",
        "OK" if has_expected else "MISSING RELEVANT",
        "OK" if not has_forbidden else "HAS FORBIDDEN",
        status
    ])

headers = [
    "Test",
    "Milestone",
    "Products Returned",
    "Relevance Check",
    "Forbidden Check",
    "Status"
]

print(tabulate(results, headers=headers, tablefmt="plain"))

passed = sum(1 for r in results if r[5] == "PASS")
print(f"\n{'='*80}")
print(f"Result: {passed}/{len(tests)} tests passed")
print("="*80 + "\n")

if passed == len(tests):
    print("SUCCESS: AI is now grounding recommendations to user's specific query.")
    print("  - Stroller query -> Travel products only (no breast pump)")
    print("  - Teething query -> Feeding/Toys products (no stroller)")
else:
    print("FAILURE: Still seeing irrelevant products.")
    print("  Check: temperature=0.9, top_p=1, strict context matching in prompt")
