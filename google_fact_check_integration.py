# google_fact_check_integration.py
import requests
import json
from datetime import datetime

class GoogleFactCheckIntegration:
    def __init__(self):
        self.api_key = "AIzaSyBXXmxWMVyeP1OCejuRneU7qX8_4ZS7Sco"
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    def fact_check(self, claim_text):
        """Fact check any claim using Google's database"""
        
        params = {
            'query': claim_text[:200],  # Limit to 200 chars
            'key': self.api_key,
            'languageCode': 'en',
            'maxAgeDays': 365,  # Search last year
            'pageSize': 5
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                return self._process_results(response.json(), claim_text)
            elif response.status_code == 403:
                return {
                    'success': False,
                    'error': 'API key invalid or quota exceeded',
                    'verdict': 'Error',
                    'confidence': 0
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'verdict': 'Error',
                    'confidence': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'verdict': 'Error',
                'confidence': 0
            }
    
    def _process_results(self, data, original_claim):
        """Process API results into user-friendly format"""
        
        if 'claims' not in data or not data['claims']:
            return {
                'success': True,
                'found': False,
                'verdict': 'Unverified',
                'confidence': 30,
                'message': 'No fact-checking articles found for this claim',
                'sources': []
            }
        
        # Get the most relevant claim
        best_match = data['claims'][0]
        reviews = best_match.get('claimReview', [])
        
        if not reviews:
            return {
                'success': True,
                'found': False,
                'verdict': 'Unverified',
                'confidence': 30,
                'message': 'No reviews available',
                'sources': []
            }
        
        # Analyze all reviews
        verdicts = []
        sources = []
        
        for review in reviews:
            rating = review.get('textualRating', '').lower()
            publisher = review.get('publisher', {}).get('name', 'Unknown')
            
            # Determine verdict from rating
            if rating in ['true', 'correct', 'accurate']:
                verdicts.append('true')
            elif rating in ['false', 'incorrect', 'pants on fire', 'fake']:
                verdicts.append('false')
            elif rating in ['mostly true', 'partly true']:
                verdicts.append('mostly_true')
            elif rating in ['mostly false', 'partly false']:
                verdicts.append('mostly_false')
            elif rating in ['half true', 'mixed']:
                verdicts.append('mixed')
            else:
                verdicts.append('unverified')
            
            sources.append({
                'publisher': publisher,
                'rating': review.get('textualRating', 'Unrated'),
                'url': review.get('url', ''),
                'title': review.get('title', ''),
                'review_date': review.get('reviewDate', '')
            })
        
        # Determine final verdict
        if any(v == 'false' for v in verdicts):
            final_verdict = 'False'
            confidence = 90
            explanation = f"Fact-checkers say this claim is false"
        elif all(v == 'true' for v in verdicts):
            final_verdict = 'True'
            confidence = 90
            explanation = f"Fact-checkers confirm this claim is true"
        elif any(v == 'mostly_false' for v in verdicts):
            final_verdict = 'Mostly False'
            confidence = 75
            explanation = f"Fact-checkers find this claim mostly false"
        elif any(v == 'mostly_true' for v in verdicts):
            final_verdict = 'Mostly True'
            confidence = 75
            explanation = f"Fact-checkers find this claim mostly true"
        elif any(v == 'mixed' for v in verdicts):
            final_verdict = 'Mixed'
            confidence = 60
            explanation = f"Fact-checkers have mixed opinions"
        else:
            final_verdict = 'Unverified'
            confidence = 40
            explanation = f"Limited fact-checking information available"
        
        return {
            'success': True,
            'found': True,
            'verdict': final_verdict,
            'confidence': confidence,
            'explanation': explanation,
            'claim_text': best_match.get('text', '')[:200],
            'claimant': best_match.get('claimant', 'Unknown'),
            'review_count': len(reviews),
            'sources': sources,
            'original_claim': original_claim
        }


# Test the integration
if __name__ == '__main__':
    checker = GoogleFactCheckIntegration()
    
    print("=" * 60)
    print("GOOGLE FACT CHECK API - REAL RESULTS")
    print("=" * 60)
    
    test_claims = [
        "Trump is president of the United States",
        "Joe Biden is the current US president",
        "Vaccines cause autism",
        "Climate change is a hoax"
    ]
    
    for claim in test_claims:
        print(f"\n📝 Claim: {claim}")
        print("-" * 40)
        
        result = checker.fact_check(claim)
        
        if result['success'] and result['found']:
            print(f"✅ VERDICT: {result['verdict']}")
            print(f"📊 CONFIDENCE: {result['confidence']}%")
            print(f"📖 {result['explanation']}")
            print(f"🔍 Fact-checked by: {result['review_count']} source(s)")
            
            for source in result['sources'][:2]:
                print(f"\n   📰 {source['publisher']}")
                print(f"   Rating: {source['rating']}")
                print(f"   🔗 {source['url'][:60]}...")
        else:
            print(f"⚠️ {result.get('message', 'No fact checks found')}")