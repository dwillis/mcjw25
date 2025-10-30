from requests_html import HTMLSession
import json
import os

# Create a session to preserve cookies
session = HTMLSession()

# Set headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Visit the URL
url = "https://www.hattiesburgamerican.com/public-notices"
response = session.get(url, headers=headers)

# The session now has the cookies from the response
print(f"Status Code: {response.status_code}")
print(f"\nCookies preserved in session:")
for cookie_name, cookie_value in session.cookies.items():
    print(f"  {cookie_name}: {cookie_value}")

# Check if we can find any clues about the API in the page content
print(f"\nFirst 1000 characters of response:")
print(response.text[:1000])

# Make POST requests to the search API with pagination
# This will automatically include the cookies from the previous request
search_url = "https://www.hattiesburgamerican.com/public-notices/api/search"

# Update headers for POST request - Content-Type must be text/plain
post_headers = headers.copy()
post_headers['Content-Type'] = 'text/plain;charset=UTF-8'
post_headers['Accept'] = '*/*'
post_headers['Referer'] = 'https://www.hattiesburgamerican.com/public-notices'
post_headers['Origin'] = 'https://www.hattiesburgamerican.com'

# Load existing results if file exists
results_file = 'notices_results.json'
existing_ids = set()
all_results = []

if os.path.exists(results_file):
    with open(results_file, 'r') as f:
        all_results = json.load(f)
        existing_ids = {item['_id'] for item in all_results}
    print(f"Loaded {len(existing_ids)} existing notice IDs")

# Paginate through all results
page = 1
total_new = 0
total_results = None

while True:
    print(f"\nFetching page {page}...")
    
    # Send the actual payload structure
    search_data = {
        "publication": None,
        "markets": ["HAT hattiesburgamerican.com", "252", "HAT Hattiesburg American"],
        "keyword": "\"request for bids\"",
        "noticeType": "",
        "state": None,
        "startDate": "2025-10-01T04:00:00.000Z",
        "endDate": None,
        "page": page
    }
    
    search_response = session.post(search_url, headers=post_headers, data=json.dumps(search_data))
    
    if search_response.status_code != 200:
        print(f"Error: Status code {search_response.status_code}")
        break
    
    results = search_response.json()
    
    if total_results is None:
        total_results = results['hits']['total']['value']
        print(f"Total results available: {total_results}")
    
    hits = results['hits']['hits']
    print(f"Results in this page: {len(hits)}")
    
    if not hits:
        print("No more results")
        break
    
    # Check for duplicates and add new results
    page_new = 0
    for hit in hits:
        if hit['_id'] not in existing_ids:
            all_results.append(hit)
            existing_ids.add(hit['_id'])
            page_new += 1
            total_new += 1
    
    print(f"New results from this page: {page_new}")
    
    # Break if we got fewer results than expected (last page)
    if len(hits) < 20:
        break
    
    page += 1

# Save updated results
with open(results_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*50}")
print(f"Total new results added: {total_new}")
print(f"Total unique notices saved: {len(all_results)}")
print(f"Results saved to: {results_file}")
