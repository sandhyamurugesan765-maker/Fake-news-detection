# api_verifier.py - Add this to your project
import os
import requests
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

class GNewsVerifier:
    def __init__(self):
        self.api_key = os.getenv('GNEWS_API_KEY')
        self.base_url = "https://gnews.io/api/v4/search"
        
        if not self.api_key:
            print("⚠️ Warning: GNEWS_API_KEY not found in .env file")
    
    def verify_claim(self, claim_text):
        """Search for real news articles related to the claim"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'No API key found. Please add GNEWS_API_KEY to .env file'
            }
        
        # Clean the query (take first 100 chars)
        query = claim_text[:100].replace('\n', ' ').strip()
        
        params = {
            'q': query,
            'apikey': self.api_key,
            'lang': 'en',
            'max': 5,
            'country': 'us',
            'sortby': 'relevance'
        }
        
        try:
            print(f"🔍 Searching GNews for: {query[:50]}...")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'articles' in data and data['articles']:
                    articles = data['articles']
                    print(f"✅ Found {len(articles)} relevant articles")
                    
                    return {
                        'success': True,
                        'verified': True,
                        'sources_found': len(articles),
                        'sources': [{
                            'title': a['title'],
                            'source': a['source']['name'],
                            'url': a['url'],
                            'published': a['publishedAt'],
                            'description': a.get('description', '')[:200]
                        } for a in articles[:3]]
                    }
                else:
                    print("❌ No matching articles found")
                    return {
                        'success': True,
                        'verified': False,
                        'sources_found': 0,
                        'message': 'No news sources found for this claim'
                    }
            else:
                print(f"❌ API Error: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API returned status code {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            print("❌ API Timeout")
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_credibility_score(self, claim_text):
        """Get credibility score based on real news sources"""
        result = self.verify_claim(claim_text)
        
        if not result.get('success'):
            return {
                'score': 50,
                'level': 'Unknown',
                'message': 'Could not verify with external sources'
            }
        
        if result.get('verified'):
            sources_count = result.get('sources_found', 0)
            
            # Calculate credibility score based on number of sources
            if sources_count >= 5:
                score = 90
                level = "High - Multiple sources confirm"
            elif sources_count >= 3:
                score = 75
                level = "Medium - Several sources found"
            elif sources_count >= 1:
                score = 60
                level = "Low - Some sources found"
            else:
                score = 40
                level = "Unverified - No sources found"
            
            return {
                'score': score,
                'level': level,
                'sources_found': sources_count,
                'sources': result.get('sources', [])
            }
        else:
            return {
                'score': 30,
                'level': 'Unverified',
                'message': 'No credible sources found'
            }

# Test function to verify API works
if __name__ == '__main__':
    print("Testing GNews API Integration...")
    verifier = GNewsVerifier()
    
    # Test with a sample claim
    test_claim = "Scientists discover new treatment for cancer"
    result = verifier.verify_claim(test_claim)
    
    print("\n" + "="*50)
    print("Test Result:")
    print("="*50)
    print(result)