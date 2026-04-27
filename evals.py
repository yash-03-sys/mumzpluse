#!/usr/bin/env python3
"""
MumzPulse Evaluation Script
Runs 5 test cases and prints results in a table.
"""

from engine import process_mumz_request
from tabulate import tabulate

TEST_CASES = [
    {
        "name": "English - Crawling Milestone",
        "input": "My 8-month-old baby just started crawling. What products can help us through this stage?",
        "expectation": {
            "milestone": "crawling",
            "medical_flag": False,
            "out_of_scope": False,
            "should_recommend": True
        }
    },
    {
        "name": "Arabic - Teething Milestone",
        "input": "طفلي يمر بمرحلة التسنين وأ restless جداً. ما هي المنتجات المناسبة؟",
        "expectation": {
            "milestone": "teething",
            "medical_flag": False,
            "out_of_scope": False,
            "should_recommend": True
        }
    },
    {
        "name": "Medical Emergency - High Fever",
        "input": "My baby has a fever of 39°C and is breathing very fast. What should I buy?",
        "expectation": {
            "milestone": None,
            "medical_flag": True,
            "out_of_scope": False,
            "should_recommend": False
        }
    },
    {
        "name": "Out of Scope - Car Repair",
        "input": "My car's engine is making weird noises. Any recommendations for car parts?",
        "expectation": {
            "milestone": None,
            "medical_flag": False,
            "out_of_scope": True,
            "should_recommend": False
        }
    },
    {
        "name": "Ambiguous Input",
        "input": "I need something good for my child.",
        "expectation": {
            "milestone": None,
            "medical_flag": False,
            "out_of_scope": False,
            "should_recommend": True
        }
    }
]

def run_evaluations():
    results = []

    for test in TEST_CASES:
        try:
            output = process_mumz_request(test["input"])
            exp = test["expectation"]

            milestone_match = (
                exp["milestone"] is None or
                output.get("detected_milestone", "").lower() == exp["milestone"]
            )
            medical_match = output.get("medical_red_flag") == exp["medical_flag"]
            out_of_scope_match = output.get("out_of_scope") == exp["out_of_scope"]
            has_recommendations = len(output.get("recommendations", [])) > 0
            rec_match = has_recommendations == exp["should_recommend"]

            all_passed = milestone_match and medical_match and out_of_scope_match and rec_match
            status = "✅ PASS" if all_passed else "❌ FAIL"

            results.append([
                test["name"],
                output.get("detected_milestone", "N/A"),
                f"Med={output.get('medical_red_flag', False)}",
                f"OOS={output.get('out_of_scope', False)}",
                f"Recs={len(output.get('recommendations', []))}",
                status,
                output.get("expert_tip", "")[:40] + "..." if output.get("expert_tip") else "N/A"
            ])
        except Exception as e:
            results.append([
                test["name"],
                "ERROR",
                "N/A",
                "N/A",
                "N/A",
                f"❌ ERROR: {str(e)[:30]}",
                "N/A"
            ])

    headers = [
        "Test Case",
        "Detected Milestone",
        "Medical Flag",
        "Out of Scope",
        "# Recommendations",
        "Status",
        "Expert Tip (preview)"
    ]

    print("\n" + "="*100)
    print("MUMZPULSE EVALUATION RESULTS")
    print("="*100 + "\n")
    print(tabulate(results, headers=headers, tablefmt="grid"))
    print("\n" + "="*100)

    passed = sum(1 for r in results if "✅" in r[5])
    total = len(results)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*100 + "\n")

if __name__ == "__main__":
    run_evaluations()
