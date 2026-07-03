import json
import time
import requests

def run_tests():
    url_base = "http://localhost:8081"
    log_entries = []
    
    def log_call(method, path, body=None):
        url = f"{url_base}{path}"
        print(f"Calling {method} {path} (Call {len(log_entries) + 1}/50)...")
        start = time.time()
        try:
            if method == "GET":
                resp = requests.get(url, timeout=10)
            elif method == "POST":
                resp = requests.post(url, json=body, timeout=10)
            latency = (time.time() - start) * 1000
            
            try:
                resp_data = resp.json()
            except Exception:
                resp_data = resp.text
                
            entry = {
                "step": len(log_entries) + 1,
                "method": method,
                "path": path,
                "request_body": body,
                "status_code": resp.status_code,
                "response_body": resp_data,
                "latency_ms": round(latency, 2)
            }
            log_entries.append(entry)
        except Exception as e:
            print(f"Error: {e}")
            log_entries.append({
                "step": len(log_entries) + 1,
                "method": method,
                "path": path,
                "request_body": body,
                "error": str(e)
            })

    # 1. healthz x 10
    for i in range(10):
        log_call("GET", "/v1/healthz")
        
    # 2. metadata x 10
    for i in range(10):
        log_call("GET", "/v1/metadata")
        
    # 3. context x 10
    # Push version 1 to 10 of a test category
    for v in range(1, 11):
        cat_payload = {
            "slug": "test_cat_loop",
            "voice": {"tone": f"peer_clinical_v{v}"},
            "offer_catalog": [{"title": f"Dental Cleaning v{v} @ ₹299"}]
        }
        log_call("POST", "/v1/context", {
            "scope": "category",
            "context_id": "test_cat_loop",
            "version": v,
            "payload": cat_payload,
            "delivered_at": "2026-07-02T12:00:00Z"
        })
        
    # 4. tick x 10
    # Call with 10 different triggers from expanded triggers list
    available_triggers = [
        "trg_013_corporate_thali_planning",
        "trg_016_kids_yoga_program_drafting",
        "trg_020_summer_demand_shift",
        "trg_022_cde_webinar_dentists",
        "trg_019_chronic_refill_grandfather",
        "trg_023_competitor_opened_dentist",
        "trg_008_curious_ask_studio11",
        "trg_015_winback_rashmi",
        "trg_025_dormancy_glamour",
        "trg_006_festival_diwali"
    ]
    for trig_id in available_triggers:
        log_call("POST", "/v1/tick", {
            "now": "2026-07-02T12:05:00Z",
            "available_triggers": [trig_id]
        })
        
    # 5. reply x 10
    # Call 1: Conversation 1 (Auto-reply Turn 2 -> Nudge)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_auto_seq_1",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Out of office auto-response.",
        "received_at": "2026-07-02T12:10:00Z",
        "turn_number": 2
    })
    # Call 2: Conversation 1 (Auto-reply Turn 3 -> Wait)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_auto_seq_1",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Out of office auto-response.",
        "received_at": "2026-07-02T12:11:00Z",
        "turn_number": 3
    })
    # Call 3: Conversation 1 (Auto-reply Turn 4 -> End)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_auto_seq_1",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Out of office auto-response.",
        "received_at": "2026-07-02T12:12:00Z",
        "turn_number": 4
    })
    
    # Call 4: Conversation 2 (Auto-reply Turn 2 -> Nudge)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_auto_seq_2",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Respond shortly...",
        "received_at": "2026-07-02T12:10:00Z",
        "turn_number": 2
    })
    # Call 5: Conversation 2 (Auto-reply Turn 3 -> Wait)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_auto_seq_2",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Respond shortly...",
        "received_at": "2026-07-02T12:11:00Z",
        "turn_number": 3
    })
    
    # Call 6: Conversation 3 (Intent Transition)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_intent_seq",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Let's do it, send the details",
        "received_at": "2026-07-02T12:15:00Z",
        "turn_number": 2
    })
    
    # Call 7: Conversation 4 (Hostile message -> End)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_hostile_seq",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Unsubscribe immediately. Stop this spam.",
        "received_at": "2026-07-02T12:20:00Z",
        "turn_number": 2
    })
    
    # Call 8: Conversation 5 (Normal peer question -> LLM check)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_normal_seq_1",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Can you summarize the patient details for me?",
        "received_at": "2026-07-02T12:25:00Z",
        "turn_number": 2
    })
    
    # Call 9: Conversation 6 (Normal peer question -> LLM check)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_normal_seq_2",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "What is the active offer on my profile?",
        "received_at": "2026-07-02T12:30:00Z",
        "turn_number": 2
    })
    
    # Call 10: Conversation 7 (Normal peer question -> LLM check)
    log_call("POST", "/v1/reply", {
        "conversation_id": "conv_normal_seq_3",
        "merchant_id": "m_001_drmeera_dentist_delhi",
        "from_role": "merchant",
        "message": "Tell me more about the kids yoga program slots",
        "received_at": "2026-07-02T12:35:00Z",
        "turn_number": 2
    })

    # Write log to file
    out_file = "endpoint_responses.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, indent=2)
    print(f"\nSaved all 50 manual call responses to {out_file} successfully.")

if __name__ == "__main__":
    run_tests()
