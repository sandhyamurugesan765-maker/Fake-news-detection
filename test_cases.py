# test_cases.py - Complete test cases for Fake News Detection System
import requests
import json

# Test the running server
def test_detection():
    """Test the detection system with various inputs"""
    
    test_cases = [
        # ===== FALSE CLAIMS (Should be detected as FAKE) =====
        {
            "input": "Trump is president of the United States!!!",
            "expected": "Fake",
            "reason": "Sensational symbols + false claim"
        },
        {
            "input": "BREAKING NEWS!!! Obama is still president!",
            "expected": "Fake",
            "reason": "Sensational symbols + false claim"
        },
        {
            "input": "Trump is president of US",
            "expected": "Fake",
            "reason": "False claim (Biden is president)"
        },
        {
            "input": "Joe Biden is NOT the president!!",
            "expected": "Fake",
            "reason": "False claim with symbols"
        },
        {
            "input": "MIRACLE CURE FOUND!!! Government hiding the truth!!!",
            "expected": "Fake",
            "reason": "ALL CAPS + multiple exclamation + conspiracy keywords"
        },
        {
            "input": "SHOCKING! SECRETS REVEALED! They don't want you to know the truth!",
            "expected": "Fake",
            "reason": "Sensational keywords + exclamation marks"
        },
        {
            "input": "Is the government hiding aliens from us???",
            "expected": "Fake",
            "reason": "Question marks + conspiracy keyword"
        },
        {
            "input": "COVID-19 vaccines have microchips!!!",
            "expected": "Fake",
            "reason": "False claim with symbols"
        },
        {
            "input": "5G towers cause coronavirus?",
            "expected": "Fake",
            "reason": "False claim with question mark"
        },
        {
            "input": "EARTH IS FLAT!!! Scientists are lying to us!",
            "expected": "Fake",
            "reason": "ALL CAPS + exclamation + false claim"
        },
        {
            "input": "Miracle pill burns fat instantly without exercise!",
            "expected": "Fake",
            "reason": "Sensational keywords + exclamation"
        },
        {
            "input": "Ancient prophecy predicts end of world next month!!!",
            "expected": "Fake",
            "reason": "Sensational claim + multiple exclamation"
        },
        {
            "input": "BREAKING: Government hiding evidence of aliens!",
            "expected": "Fake",
            "reason": "Sensational keywords + exclamation"
        },
        {
            "input": "CONSPIRACY!!! The election was stolen!",
            "expected": "Fake",
            "reason": "ALL CAPS + conspiracy keyword + exclamation"
        },
        
        # ===== TRUE CLAIMS (Should be detected as REAL) =====
        {
            "input": "Joe Biden is president of the United States",
            "expected": "Real",
            "reason": "Factually correct, no symbols"
        },
        {
            "input": "Donald Trump was president from 2017 to 2021",
            "expected": "Real",
            "reason": "Factually correct historical fact"
        },
        {
            "input": "The Earth orbits the Sun",
            "expected": "Real",
            "reason": "Scientific fact"
        },
        {
            "input": "Water boils at 100 degrees Celsius at sea level",
            "expected": "Real",
            "reason": "Scientific fact"
        },
        {
            "input": "Scientists say climate change is real and caused by humans",
            "expected": "Real",
            "reason": "Contains credible indicators"
        },
        {
            "input": "According to study shows, regular exercise improves heart health",
            "expected": "Real",
            "reason": "Contains credible keyword 'study shows'"
        },
        {
            "input": "Research indicates that smoking causes lung cancer",
            "expected": "Real",
            "reason": "Contains credible keyword 'research indicates'"
        },
        {
            "input": "The United Nations was established in 1945",
            "expected": "Real",
            "reason": "Historical fact"
        },
        {
            "input": "NASA confirms water exists on Mars",
            "expected": "Real",
            "reason": "Scientific fact from credible source"
        },
        
        # ===== SUSPICIOUS/MIXED (Should be marked for verification) =====
        {
            "input": "Joe Biden is president!",
            "expected": "Suspicious",
            "reason": "True claim but has exclamation mark"
        },
        {
            "input": "Is Joe Biden the current president?",
            "expected": "Suspicious",
            "reason": "True claim but has question mark"
        },
        {
            "input": "Trump was president!!!",
            "expected": "Suspicious",
            "reason": "True claim but has multiple exclamation marks"
        },
        {
            "input": "BREAKING: New cancer treatment approved!",
            "expected": "Suspicious",
            "reason": "May be true but uses sensational formatting"
        },
        
        # ===== EDGE CASES =====
        {
            "input": "",
            "expected": "Error",
            "reason": "Empty input"
        },
        {
            "input": "???",
            "expected": "Fake",
            "reason": "Only question marks - sensational"
        },
        {
            "input": "!!!",
            "expected": "Fake",
            "reason": "Only exclamation marks - sensational"
        },
        {
            "input": "NORMAL TEXT WITH NO SYMBOLS",
            "expected": "Real",
            "reason": "No sensational indicators"
        },
        {
            "input": "This is a normal sentence without any sensational elements.",
            "expected": "Real",
            "reason": "Normal text, no symbols"
        }
    ]
    
    print("=" * 80)
    print("FAKE NEWS DETECTION SYSTEM - TEST CASES")
    print("=" * 80)
    
    # Statistics
    passed = 0
    failed = 0
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['input'][:60]}")
        print(f"Expected: {test['expected']}")
        print(f"Reason: {test['reason']}")
        print("-" * 40)
        
        # Here you would call your actual detection function
        # For now, we'll simulate based on rules
        result = simulate_detection(test['input'])
        
        # Check if result matches expected
        if test['expected'] in result['prediction']:
            print(f"✅ PASSED | Got: {result['prediction']}")
            passed += 1
            results.append({"test": test, "result": result, "passed": True})
        else:
            print(f"❌ FAILED | Got: {result['prediction']}")
            failed += 1
            results.append({"test": test, "result": result, "passed": False})
        
        print(f"   Confidence: {result['confidence']:.1f}%")
        print(f"   Sensational Score: {result.get('sensational_score', 0)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {(passed/len(test_cases)*100):.1f}%")
    
    # Show failed tests
    if failed > 0:
        print("\n" + "=" * 80)
        print("FAILED TESTS DETAILS")
        print("=" * 80)
        for item in results:
            if not item['passed']:
                test = item['test']
                result = item['result']
                print(f"\nInput: {test['input']}")
                print(f"Expected: {test['expected']}")
                print(f"Got: {result['prediction']}")
                print(f"Reason: {test['reason']}")
    
    return passed, failed, results


def simulate_detection(text):
    """Simulate the detection logic from simple_app.py"""
    
    if not text or not text.strip():
        return {
            'prediction': 'Error - Empty Input',
            'confidence': 0,
            'sensational_score': 0
        }
    
    # Check for sensational symbols
    has_exclamation = '!' in text
    has_question = '?' in text
    has_multiple_exclamation = '!!' in text or '!!!' in text
    has_multiple_question = '??' in text or '???' in text
    
    # Check for ALL CAPS
    words = text.split()
    caps_words = sum(1 for word in words if word.isupper() and len(word) > 2)
    
    # Calculate sensational score
    sensational_score = 0
    if has_exclamation:
        sensational_score += 20
    if has_question:
        sensational_score += 15
    if has_multiple_exclamation:
        sensational_score += 25
    if has_multiple_question:
        sensational_score += 20
    if caps_words > 2:
        sensational_score += min(caps_words * 5, 30)
    
    text_lower = text.lower()
    
    # Check factual accuracy
    is_false_claim = False
    
    # False claims database
    false_claims = [
        'trump is president', 'obama is president', 'bush is president',
        'biden is not president', 'earth is flat', 'vaccines cause autism',
        '5g causes covid', 'government hiding aliens', 'election was stolen'
    ]
    
    for claim in false_claims:
        if claim in text_lower:
            is_false_claim = True
            break
    
    # Determine prediction
    if is_false_claim and sensational_score >= 20:
        prediction = 'Fake (False Claim + Sensational)'
        confidence = 95
    elif is_false_claim:
        prediction = 'Fake (False Claim)'
        confidence = 90
    elif sensational_score >= 40:
        prediction = 'Fake (Sensational Content)'
        confidence = min(70 + sensational_score/2, 95)
    elif sensational_score >= 20:
        prediction = 'Suspicious - Verify'
        confidence = 55
    elif sensational_score == 0 and not is_false_claim:
        prediction = 'Likely Real'
        confidence = 75
    else:
        prediction = 'Real'
        confidence = 70
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'sensational_score': sensational_score,
        'has_exclamation': has_exclamation,
        'has_question': has_question,
        'caps_words': caps_words
    }


def test_with_live_server():
    """Test with your running server (if available)"""
    
    try:
        # Test if server is running
        response = requests.get('http://localhost:8000', timeout=2)
        print("✅ Server is running on http://localhost:8000")
        
        # Test claims via API (if you have an API endpoint)
        test_claims = [
            "Trump is president!!!",
            "Joe Biden is president",
            "BREAKING NEWS!!"
        ]
        
        print("\nTesting with live server...")
        for claim in test_claims:
            print(f"\nClaim: {claim}")
            # Note: This assumes you have an API endpoint
            # For now, just showing what would be sent
            print(f"  Would send to /detect endpoint")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python simple_app.py")
    except Exception as e:
        print(f"Error: {e}")


# Quick reference guide
def print_quick_reference():
    """Print quick reference for test cases"""
    
    print("\n" + "=" * 80)
    print("QUICK REFERENCE - What to Expect")
    print("=" * 80)
    
    examples = [
        ("Trump is president!!!", "FAKE", "Sensational symbols + false claim"),
        ("Trump is president", "FAKE", "False claim (Biden is president)"),
        ("Joe Biden is president", "REAL", "Factually correct"),
        ("BREAKING NEWS!!!", "FAKE", "Sensational content"),
        ("Is the earth flat???", "FAKE", "False claim + question marks"),
        ("Joe Biden is president!", "SUSPICIOUS", "True claim but has exclamation"),
        ("The sky is blue", "REAL", "Normal text, no symbols"),
    ]
    
    print("\n| Input | Expected Result | Reason |")
    print("|-------|----------------|--------|")
    for inp, res, reason in examples:
        print(f"| {inp[:30]:30} | {res:14} | {reason} |")


if __name__ == '__main__':
    print("🔍 FAKE NEWS DETECTOR - TEST SUITE")
    print("=" * 80)
    
    # Run the tests
    passed, failed, results = test_detection()
    
    # Print quick reference
    print_quick_reference()
    
    # Test live server
    print("\n" + "=" * 80)
    test_with_live_server()
    
    print("\n" + "=" * 80)
    print("HOW TO RUN YOUR SERVER AND TEST:")
    print("=" * 80)
    print("1. Start your server: python simple_app.py")
    print("2. Open browser to: http://localhost:8000")
    print("3. Create an account and login")
    print("4. Test these examples in the Detect page")
    print("=" * 80)