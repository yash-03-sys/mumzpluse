#!/usr/bin/env python3
"""
Test script to verify dynamic variability between two different queries.
"""

from engine import process_mumz_request

queries = [
    "My 8-month-old is starting to eat solids but is very picky and I'm worried about allergies.",
    "My baby just started crawling and I'm scared she'll hurt herself on the stairs."
]

print("\n" + "="*80)
print("VARIABILITY TEST – Comparing Two Different Queries")
print("="*80 + "\n")

results = []
for i, query in enumerate(queries, 1):
    result = process_mumz_request(query)
    
    milestone = result.get('detected_milestone', 'N/A')
    expert_tip = result.get('expert_tip', '')
    word_count = len(expert_tip.split()) if expert_tip else 0
    rec_names = [r['name'] for r in result.get('recommendations', [])]
    
    results.append({
        'query': query,
        'milestone': milestone,
        'word_count': word_count,
        'recommendations': rec_names,
        'expert_tip_preview': expert_tip[:100] + "..." if len(expert_tip) > 100 else expert_tip
    })
    
    print(f"Query {i}: {query}")
    print(f"  Milestone: {milestone}")
    print(f"  Word Count: {word_count}")
    print(f"  Recommendations: {', '.join(rec_names)}")
    print(f"  Expert Tip (first 100 chars): {expert_tip[:100]}...")
    print()

# Check variability
milestones_differ = results[0]['milestone'] != results[1]['milestone']
word_counts_differ = abs(results[0]['word_count'] - results[1]['word_count']) > 10
recs_differ = set(results[0]['recommendations']) != set(results[1]['recommendations'])
tips_differ = results[0]['expert_tip_preview'] != results[1]['expert_tip_preview']

print("="*80)
print("VARIABILITY CHECK:")
print(f"  Milestones differ: {'✅ YES' if milestones_differ else '❌ NO (same milestone detected')}")
print(f"  Word count variance: {'✅ >10 words' if word_counts_differ else '⚠️ Similar lengths'}")
print(f"  Recommendations differ: {'✅ YES' if recs_differ else '❌ NO (same products')}")
print(f"  Tips unique: {'✅ YES' if tips_differ else '❌ NO (repetitive text')}")
print("="*80 + "\n")

if milestones_differ and word_counts_differ and tips_differ:
    print("✅ SUCCESS: AI is generating dynamic, context-aware responses.")
else:
    print("⚠️  WARNING: Some similarity detected. Try more varied inputs.")
