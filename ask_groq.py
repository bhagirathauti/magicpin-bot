import json
import os
import requests

def main():
    api_key = os.getenv("GROQ_API_KEY", "")
    model = "llama-3.3-70b-versatile"

    if not api_key:
        print("Missing GROQ_API_KEY environment variable.")
        return
    
    # Read bot.py code
    with open("bot.py", "r", encoding="utf-8") as f:
        bot_code = f.read()
        
    prompt = f"""You are a Principal AI Engineer reviewing our candidate bot code (Vera) for the magicpin AI challenge.
Below is the complete implementation of our stateful FastAPI server in `bot.py`.
Please review the code and suggest concrete, highly actionable recommendations to make our bot better.

Specifically focus on:
1. **Dynamic Context-Driven Composition**: How can we make better use of advanced performance signals (e.g., delta CTRs), customer retention stats, and review themes (e.g., wait time sentiments) inside our LLM prompts?
2. **Robustness & Edge Cases**: How to handle multi-trigger ticks, rapid version updates on context pushes, state cleaning on teardown.
3. **Dialogue Flow Improvements**: Enhancing auto-reply counting, intent detection thresholds, or multi-turn context tracking.
4. **Performance & Reliability**: Optimizing rate-limits (429 handling), response caching, and prompt token efficiency.

Here is our current `bot.py` code:
```python
{bot_code}
```
Provide your analysis in Markdown format. Keep it sharp, technical, and directly actionable!"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    print("Querying Llama 3.3 via Groq for recommendations...")
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an expert AI software architect and evaluator for conversational agents."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            out_file = "optimization_suggestions.md"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Suggestions saved successfully to {out_file}.")
        else:
            print(f"Failed to query Groq: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error querying Groq: {e}")

if __name__ == "__main__":
    main()
