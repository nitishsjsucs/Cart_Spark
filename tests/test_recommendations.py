"""
Unit tests for CartSpark recommendation system
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import load_model, rank, _pair

# Load model once for all tests
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'Retail', 
                        'CMPE256_Hackathon_market_basket_analysis_Release.csv')
model = load_model(CSV_PATH)

def test_model_loaded():
    """Test that model loads successfully"""
    assert model is not None
    assert len(model.catalog) > 0
    assert model.total_tx > 0
    assert len(model.top_pairs_per_item) > 0
    print("✓ test_model_loaded passed")

def test_single_item_recommendations():
    """Test recommendations for single item cart"""
    cart = ["Bosch B5512 Control Panel (SKU: B5512)"]
    recs = rank(cart, model, top_k=5)
    
    assert len(recs) > 0, "Should return recommendations"
    assert len(recs) <= 5, "Should not exceed top_k"
    assert all(r['candidate_item'] not in cart for r in recs), "Should not recommend cart items"
    assert all('lift_sum' in r for r in recs), "Should include lift_sum"
    assert all('cooccurrence_count_sum' in r for r in recs), "Should include cooccurrence"
    print("✓ test_single_item_recommendations passed")

def test_multi_item_recommendations():
    """Test recommendations for multi-item cart"""
    cart = [
        "Bosch B5512 Control Panel (SKU: B5512)",
        "Hanwha QNV-6010R Network Camera (SKU: QNV-6010R)"
    ]
    recs = rank(cart, model, top_k=8)
    
    assert len(recs) > 0, "Should return recommendations"
    rec_items = [r['candidate_item'] for r in recs]
    assert not any(item in rec_items for item in cart), "Should not recommend cart items"
    print("✓ test_multi_item_recommendations passed")

def test_no_self_recommendations():
    """Ensure items in cart are never recommended"""
    cart = ["Bosch B5512 Control Panel (SKU: B5512)", 
            "Hanwha QNV-6010R Network Camera (SKU: QNV-6010R)",
            "DSC WS4916 Smoke Detector (SKU: WS4916)"]
    recs = rank(cart, model, top_k=10)
    
    rec_items = [r['candidate_item'] for r in recs]
    for cart_item in cart:
        assert cart_item not in rec_items, f"Cart item {cart_item} should not be recommended"
    print("✓ test_no_self_recommendations passed")

def test_ranking_order():
    """Test that recommendations are sorted by lift_sum descending"""
    cart = ["Bosch B5512 Control Panel (SKU: B5512)"]
    recs = rank(cart, model, top_k=10)
    
    if len(recs) > 1:
        lifts = [r['lift_sum'] for r in recs]
        assert lifts == sorted(lifts, reverse=True), "Recommendations should be sorted by lift_sum"
    print("✓ test_ranking_order passed")

def test_empty_cart():
    """Test graceful handling of empty cart"""
    recs = rank([], model, top_k=5)
    assert recs == [], "Empty cart should return empty recommendations"
    print("✓ test_empty_cart passed")

def test_invalid_cart_items():
    """Test handling of cart with non-existent items"""
    cart = ["NonExistentItem123", "AnotherFakeItem456"]
    recs = rank(cart, model, top_k=5)
    assert recs == [], "Invalid items should return empty recommendations"
    print("✓ test_invalid_cart_items passed")

def test_pair_function():
    """Test pair ordering is consistent"""
    assert _pair("A", "B") == _pair("B", "A"), "Pair order should be consistent"
    assert _pair("A", "B") == ("A", "B"), "Pair should be alphabetically sorted"
    assert _pair("Z", "A") == ("A", "Z"), "Pair should be alphabetically sorted"
    print("✓ test_pair_function passed")

def test_recommendation_structure():
    """Test that recommendation objects have required fields"""
    cart = ["Bosch B5512 Control Panel (SKU: B5512)"]
    recs = rank(cart, model, top_k=3)
    
    if recs:
        rec = recs[0]
        assert 'candidate_item' in rec, "Should have candidate_item"
        assert 'lift_sum' in rec, "Should have lift_sum"
        assert 'cooccurrence_count_sum' in rec, "Should have cooccurrence_count_sum"
        assert 'support' in rec, "Should have support"
        assert 'reasons' in rec, "Should have reasons"
        assert isinstance(rec['reasons'], list), "Reasons should be a list"
    print("✓ test_recommendation_structure passed")

def test_top_k_parameter():
    """Test that top_k parameter is respected"""
    cart = ["Bosch B5512 Control Panel (SKU: B5512)"]
    
    recs_5 = rank(cart, model, top_k=5)
    recs_10 = rank(cart, model, top_k=10)
    
    assert len(recs_5) <= 5, "Should respect top_k=5"
    assert len(recs_10) <= 10, "Should respect top_k=10"
    
    if len(recs_5) == 5 and len(recs_10) >= 5:
        # First 5 should be the same
        for i in range(5):
            assert recs_5[i]['candidate_item'] == recs_10[i]['candidate_item'], \
                "Top items should be consistent across different top_k values"
    print("✓ test_top_k_parameter passed")

def test_performance():
    """Test that recommendations are generated quickly"""
    import time
    cart = ["Bosch B5512 Control Panel (SKU: B5512)"]
    
    start = time.time()
    recs = rank(cart, model, top_k=8)
    duration = time.time() - start
    
    assert duration < 0.1, f"Recommendations should be fast (<100ms), took {duration*1000:.2f}ms"
    print(f"✓ test_performance passed (took {duration*1000:.2f}ms)")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Running CartSpark Unit Tests")
    print("="*60 + "\n")
    
    tests = [
        test_model_loaded,
        test_single_item_recommendations,
        test_multi_item_recommendations,
        test_no_self_recommendations,
        test_ranking_order,
        test_empty_cart,
        test_invalid_cart_items,
        test_pair_function,
        test_recommendation_structure,
        test_top_k_parameter,
        test_performance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
        sys.exit(1)
