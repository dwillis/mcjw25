import json
import llm
import argparse

# CLI: allow a --limit to process only the first N notices (useful for testing)
parser = argparse.ArgumentParser(description='Process public notices with an LLM')
parser.add_argument('--limit', type=int, default=0, help='Limit processing to first N notices (0 = all)')
args = parser.parse_args()

# Load the notices
with open('notices_results.json', 'r') as f:
    notices = json.load(f)

total_notices = len(notices)
if args.limit and args.limit > 0:
    notices = notices[: args.limit]

print(f"Processing {len(notices)} notices (out of {total_notices})...")

# Initialize the model
model = llm.get_model("claude-haiku-4.5")

processed_notices = []

for i, notice in enumerate(notices, 1):
    print(f"Processing notice {i}/{len(notices)}...")
    
    text = notice['_source']['text']
    
    # Create the prompt
    prompt = f"""Analyze this public notice and extract the following information in JSON format:

- agency: The government agency or organization issuing the notice
- docket_no: The docket or case number (if any)
- description: A brief 1-2 sentence description of what this notice is about
- category: A 1-2 word category (e.g., "Oil & Gas", "Estate", "Construction Bid", "Legal Summons", etc.)
- key_dates: An array of objects with "date" and "event" for important dates mentioned
- newsworthiness: A score from 1-10 (10 being highest) based on public interest, impact, and urgency

Public Notice Text:
{text}

Return ONLY valid JSON with no additional text."""

    # Get response from LLM
    response = model.prompt(prompt)
    
    try:
        # Get the response text and strip markdown code blocks if present
        response_text = response.text().strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()
        
        # Parse the JSON response
        analysis = json.loads(response_text)
        
        # Add the original ID and metadata
        processed_notice = {
            "_id": notice['_id'],
            "publication": notice['_source']['publication'],
            "date_start": notice['_source']['date_start'],
            "date_end": notice['_source']['date_end'],
            **analysis
        }
        
        processed_notices.append(processed_notice)
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for notice {notice['_id']}: {e}")
        print(f"Response: {response.text()}")
        # Add a basic record so we don't lose track
        processed_notices.append({
            "_id": notice['_id'],
            "error": "Failed to parse LLM response",
            "raw_response": response.text()
        })

# Save the processed notices
with open('processed_notices.json', 'w') as f:
    json.dump(processed_notices, f, indent=2)

print(f"\nProcessed {len(processed_notices)} notices")
print("Results saved to: processed_notices.json")
