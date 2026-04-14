# test_api.py
import requests

API_KEY = "AIzaSyBXXmxWMVyeP1OCejuRneU7qX8_4ZS7Sco"

# Test with a political claim
url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
params = {
    'query': "Trump is president of the United States",
    'key': API_KEY,
    'languageCode': 'en'
}

print("Testing Google Fact Check API...")
print("=" * 50)

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    if 'claims' in data and data['claims']:
        print(f"✅ Found {len(data['claims'])} fact-checked claims!\n")
        
        for claim in data['claims'][:2]:
            print(f"Claim: {claim['text'][:150]}...")
            print(f"Claimant: {claim.get('claimant', 'Unknown')}")
            
            for review in claim.get('claimReview', []):
                publisher = review.get('publisher', {}).get('name', 'Unknown')
                rating = review.get('textualRating', 'No rating')
                print(f"  → {publisher} rates this as: {rating}")
                print(f"  → Source: {review.get('url', 'N/A')[:80]}...")
            print()
    else:
        print("No fact checks found for this claim")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("=" * 50)