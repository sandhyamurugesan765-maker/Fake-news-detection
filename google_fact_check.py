# google_fact_check.py
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class GoogleFactCheckAPI:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        
        if not self.api_key:
            print("⚠️ Warning: GOOGLE_FACT_CHECK_API_KEY not found in .env file")
            print("Get your free API key from: https://console.cloud.google.com")
    
    def search_claims(self, query, language_code='en', max_age_days=90, page_size=10):
        """
        Search for fact-checked claims
        
        Parameters:
        - query: The claim text to search for
        - language_code: BCP-47 language code (e.g., 'en-US', 'hi-IN')
        - max_age_days: Maximum age of search results in days
        - page_size: Number of results to return (max 10)
        """
        if not self.api_key:
            return {'error': 'No API key configured'}
        
        params = {
            'query': query,
            'key': self.api_key,
            'languageCode': language_code,
            'maxAgeDays': max_age_days,
            'pageSize': min(page_size, 10)  # API max is 10
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                return {
                    'error': f'API Error: {response.status_code}',
                    'message': response.text
                }
                
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_response(self, data):
        """Parse the API response into a usable format"""
        if 'claims' not in data or not data['claims']:
            return {
                'success': True,
                'found': False,
                'message': 'No fact checks found for this claim'
            }
        
        claims_result = []
        
        for claim in data['claims'][:3]:  # Get top 3 results
            claim_text = claim.get('text', '')
            claimant = claim.get('claimant', 'Unknown')
            claim_date = claim.get('claimDate', '')
            
            # Get claim reviews
            reviews = []
            for review in claim.get('claimReview', []):
                reviews.append({
                    'publisher': review.get('publisher', {}).get('name', 'Unknown'),
                    'url': review.get('url', ''),
                    'title': review.get('title', ''),
                    'review_date': review.get('reviewDate', ''),
                    'textual_rating': review.get('textualRating', 'Unrated'),
                    'language': review.get('languageCode', 'en')
                })
            
            # Determine overall verdict
            verdict = self._determine_verdict(reviews)
            
            claims_result.append({
                'claim_text': claim_text[:200],
                'claimant': claimant,
                'claim_date': claim_date,
                'verdict': verdict,
                'reviews': reviews,
                'review_count': len(reviews)
            })
        
        return {
            'success': True,
            'found': True,
            'total_claims': len(claims_result),
            'claims': claims_result
        }
    
    def _determine_verdict(self, reviews):
        """Determine overall verdict from multiple reviews"""
        ratings = []
        for review in reviews:
            rating = review.get('textual_rating', '').lower()
            if rating in ['true', 'correct', 'accurate']:
                ratings.append('true')
            elif rating in ['false', 'incorrect', 'pants on fire', 'fake']:
                ratings.append('false')
            elif rating in ['mostly true', 'partly true']:
                ratings.append('mostly_true')
            elif rating in ['mostly false', 'partly false']:
                ratings.append('mostly_false')
            elif rating in ['half true', 'mixed']:
                ratings.append('mixed')
        
        if not ratings:
            return 'Unverified'
        
        if all(r == 'true' for r in ratings):
            return 'True'
        elif any(r == 'false' for r in ratings):
            return 'False'
        elif 'mostly_false' in ratings:
            return 'Mostly False'
        elif 'mostly_true' in ratings:
            return 'Mostly True'
        elif 'mixed' in ratings:
            return 'Mixed'
        else:
            return 'Unverified'
    
    def fact_check_claim(self, claim_text):
        """Main method to fact-check a claim"""
        result = self.search_claims(claim_text)
        
        if not result.get('success'):
            return {
                'verdict': 'Error',
                'confidence': 0,
                'explanation': f"API Error: {result.get('error', 'Unknown error')}",
                'sources': []
            }
        
        if not result.get('found'):
            return {
                'verdict': 'Unverified',
                'confidence': 30,
                'explanation': 'No fact-checking articles found for this claim. Try rephrasing or check news sources.',
                'sources': []
            }
        
        # Get the best match
        best_claim = result['claims'][0]
        verdict = best_claim['verdict']
        
        # Calculate confidence based on number of reviews
        review_count = best_claim['review_count']
        if review_count >= 3:
            confidence = 90
        elif review_count >= 2:
            confidence = 75
        else:
            confidence = 60
        
        # Adjust confidence based on verdict
        if verdict == 'True':
            confidence = min(confidence + 10, 95)
        elif verdict == 'False':
            confidence = min(confidence + 15, 95)
        
        # Prepare sources
        sources = []
        for review in best_claim['reviews']:
            sources.append({
                'publisher': review['publisher'],
                'url': review['url'],
                'rating': review['textual_rating'],
                'review_date': review['review_date']
            })
        
        return {
            'verdict': verdict,
            'confidence': confidence,
            'explanation': f"Fact-checked by {sources[0]['publisher'] if sources else 'fact-checking organizations'}",
            'claim_text': best_claim['claim_text'],
            'claimant': best_claim['claimant'],
            'sources': sources
        }


# Test the API
if __name__ == '__main__':
    fact_checker = GoogleFactCheckAPI()
    
    # Test claims
    test_claims = [
        "Trump is president of the United States",
        "Joe Biden is the current US president",
        "Vaccines cause autism",
        "Climate change is a hoax"
    ]
    
    print("=" * 60)
    print("Google Fact Check Tools API Test")
    print("=" * 60)
    
    for claim in test_claims:
        print(f"\n📝 Claim: {claim}")
        print("-" * 40)
        
        result = fact_checker.fact_check_claim(claim)
        
        print(f"✅ Verdict: {result['verdict']}")
        print(f"📊 Confidence: {result['confidence']}%")
        print(f"📖 Explanation: {result['explanation']}")
        
        if result['sources']:
            print(f"🔗 Sources:")
            for source in result['sources'][:2]:
                print(f"   - {source['publisher']}: {source['rating']}")
                print(f"     {source['url']}")