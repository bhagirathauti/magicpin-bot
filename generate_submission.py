import json
from pathlib import Path
import bot

def main():
    print("Generating submission.jsonl...")
    workspace_dir = Path(__file__).parent.resolve()
    expanded_dir = workspace_dir / "dataset" / "expanded"
    
    # 1. Load test pairs
    with open(expanded_dir / "test_pairs.json", "r", encoding="utf-8") as f:
        test_pairs = json.load(f)["pairs"]
        
    # 2. Pre-load all contexts into bot.contexts store
    # Load categories
    for cat_file in (expanded_dir / "categories").glob("*.json"):
        with open(cat_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            bot.contexts[("category", data["slug"])] = {"version": 1, "payload": data}
            
    # Load merchants
    for merch_file in (expanded_dir / "merchants").glob("*.json"):
        with open(merch_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            bot.contexts[("merchant", data["merchant_id"])] = {"version": 1, "payload": data}
            
    # Load customers
    for cust_file in (expanded_dir / "customers").glob("*.json"):
        with open(cust_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            bot.contexts[("customer", data["customer_id"])] = {"version": 1, "payload": data}
            
    # Load triggers
    for trig_file in (expanded_dir / "triggers").glob("*.json"):
        with open(trig_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            bot.contexts[("trigger", data["id"])] = {"version": 1, "payload": data}
            
    print(f"Loaded {len(bot.contexts)} contexts into memory.")
    
    # 3. Process each pair
    submission_lines = []
    for pair in test_pairs:
        test_id = pair["test_id"]
        trigger_id = pair["trigger_id"]
        merchant_id = pair["merchant_id"]
        customer_id = pair.get("customer_id")
        
        trigger = bot.contexts[("trigger", trigger_id)]["payload"]
        merchant = bot.contexts[("merchant", merchant_id)]["payload"]
        category = bot.contexts[("category", merchant["category_slug"])]["payload"]
        customer = bot.contexts[("customer", customer_id)]["payload"] if customer_id else None
        
        # Compose using LLM if keys are available, otherwise use rule-based fallback
        composed = {}
        provider, api_key, model = bot.get_llm_config()
        if api_key:
            system_instruction = """You are Vera, magicpin's merchant AI assistant.
Respond ONLY with a JSON object containing: body, cta, send_as, suppression_key, rationale."""
            prompt = f"""=== CONTEXT ===
Category: {json.dumps(category)}
Merchant: {json.dumps(merchant)}
Trigger: {json.dumps(trigger)}
Customer: {json.dumps(customer) if customer else 'None'}
"""
            composed = bot.call_llm(system_instruction, prompt)
            
        required_keys = {"body", "cta", "send_as", "suppression_key", "rationale"}
        if not composed or not required_keys.issubset(composed.keys()):
            composed = bot.get_rule_based_composition(category, merchant, trigger, customer)
            
        line = {
            "test_id": test_id,
            "body": composed["body"],
            "cta": composed["cta"],
            "send_as": composed["send_as"],
            "suppression_key": composed["suppression_key"],
            "rationale": composed["rationale"]
        }
        submission_lines.append(line)
        print(f"Composed {test_id} for trigger {trigger_id}")
        
    # 4. Write submission.jsonl
    out_path = workspace_dir / "submission.jsonl"
    with open(out_path, "w", encoding="utf-8") as f:
        for line in submission_lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
            
    print(f"Generated submission.jsonl at {out_path} with {len(submission_lines)} lines.")

if __name__ == "__main__":
    main()
