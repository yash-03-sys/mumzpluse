#!/usr/bin/env python3
"""
Quick smoke test – verifies core modules load and engine initializes.
Run: python validate.py
"""

import sys

print("="*60)
print("MUMZPULSE VALIDATION")
print("="*60)

# Test 1: engine.py imports
try:
    from engine import MumzPulseEngine, process_mumz_request
    print("[PASS] engine.py imports successfully")
except Exception as e:
    print(f"[FAIL] engine.py import error: {e}")
    sys.exit(1)

# Test 2: Engine initializes (loads catalog + Groq client)
try:
    engine = MumzPulseEngine()
    print(f"[PASS] MumzPulseEngine initialized ({len(engine.catalog)} products loaded)")
except Exception as e:
    print(f"[FAIL] Engine init error: {e}")
    sys.exit(1)

# Test 3: Catalog has required fields
required_fields = ['name', 'category', 'benefit', 'expert_insights']
for product in engine.catalog:
    for field in required_fields:
        if field not in product:
            print(f"[FAIL] Product {product.get('sku','?')} missing field: {field}")
            sys.exit(1)
print(f"[PASS] All {len(engine.catalog)} products have required fields + expert_insights")

# Test 4: Quick inference (requires GROQ_API_KEY in .env)
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "your_groq_api_key_here":
    print("[SKIP] GROQ_API_KEY not configured – skipping live inference test")
else:
    try:
        result = process_mumz_request("My baby is crawling")
        assert 'detected_milestone' in result
        assert 'recommendations' in result
        assert 'expert_tip' in result
        assert len(result.get('expert_tip', '')) > 50  # At least 50 chars
        print(f"[PASS] Live inference: milestone='{result['detected_milestone']}', tip length={len(result['expert_tip'])} chars")
    except Exception as e:
        print(f"[FAIL] Inference error: {e}")
        sys.exit(1)

print("="*60)
print("✅ ALL CHECKS PASSED – Ready to run streamlit run main.py")
print("="*60)
