# Milestone-Based Instructions: magicpin AI Challenge

This file lists the concrete steps required to build our merchant AI assistant (**Vera**) and successfully pass the evaluation harness.

---

## Milestone 1: Dataset Generation & Prep
1. **Expand the Dataset**:
   Run the dataset generator script to expand seeds into the full mock dataset of 50 merchants, 200 customers, and 100 triggers:
   ```bash
   python dataset/generate_dataset.py --out ./dataset/expanded
   ```
2. **Verify Expanded Files**:
   Ensure `dataset/expanded/` contains:
   - `categories/` (5 files)
   - `merchants/` (50 files)
   - `customers/` (200 files)
   - `triggers/` (100 files)
   - `test_pairs.json` (30 test pairs)

---

## Milestone 2: Exposing the API Server (`bot.py`)
1. **Install Dependencies**:
   Ensure `fastapi` and `uvicorn` are installed:
   ```bash
   pip install fastapi uvicorn pydantic requests
   ```
2. **Implement API Boilerplate**:
   Create a Python file named `bot.py` and implement the 5 endpoints with exact routing:
   - `GET /v1/healthz`
   - `GET /v1/metadata`
   - `POST /v1/context`
   - `POST /v1/tick`
   - `POST /v1/reply`
3. **Verify Server Functionality**:
   Run the server locally:
   ```bash
   uvicorn bot:app --host 0.0.0.0 --port 8080
   ```
   Test with simple curl commands (e.g. `curl http://localhost:8080/v1/healthz`).

---

## Milestone 3: Context Storage & Version Management
1. **Design Context Storage**:
   Implement an in-memory dictionary-based storage in `bot.py` keyed by `(scope, context_id)`.
2. **Ensure Version Idempotency**:
   Verify that `POST /v1/context`:
   - Replaces existing context with new values if the pushed `version` is strictly higher.
   - Rejects the request with HTTP `409 Conflict` (or JSON response `{"accepted": false, "reason": "stale_version"}`) if the version is less than or equal to the stored version.
3. **Add Retrieval Helpers**:
   Write utility functions to fetch and assemble category, merchant, customer, and trigger contexts based on ID references.

---

## Milestone 4: Compose Engine & Prompt Engineering
1. **Integrate Gemini API Client**:
   Implement LLM client calling to Gemini using the system environment API keys.
2. **Construct Composer Prompts**:
   Create structured prompts using the 4-context model fields:
   - Format: `compose(category, merchant, trigger, customer?) -> ComposedMessage`
   - Prompt constraints: Specificity (concrete numbers/page references), Category fit (peer clinical voice for dentists, operator voice for restaurants), single CTA, Hindi-English mixing as preferred, no URLs, no hallucinations.
3. **Validate Message Payload**:
   Ensure `/v1/tick` returns actions structured with `conversation_id`, `merchant_id`, `customer_id`, `send_as`, `trigger_id`, `body`, `cta`, `suppression_key`, and `rationale`.

---

## Milestone 5: Dialogue Flow & Replay Handling
1. **Implement Auto-Reply Detection**:
   Store conversation message history. If the incoming merchant message matches the same auto-reply text multiple times in a row, backoff with a `wait` action, and exit with `end` after 3-4 repeats.
2. **Implement Intent Transition**:
   Detect merchant intent cues such as "let's do it" or "confirm" and switch instantly from pitching/qualifying to action-execution (e.g. drafting WhatsApp message template, setting up GBP post).
3. **Implement Hostile Message Handling**:
   Gracefully end conversations when the user requests to opt-out, stop messaging, or uses hostile language.

---

## Milestone 6: Local Validation via Judge Simulator
1. **Setup LLM Provider**:
   Configure the credentials inside `judge_simulator.py` (e.g., API key, LLM model).
2. **Run Local Simulations**:
   Execute the evaluation scenarios:
   ```bash
   python judge_simulator.py
   ```
3. **Optimize & Refine**:
   Check scores and rationale outputted by the judge. Adjust the LLM system prompt templates in `bot.py` to maximize performance.

---

## Milestone 7: Submission Preparation
1. **Generate Test Output**:
   Run the bot's composer logic on the 30 canonical pairs specified in `test_pairs.json` and export the results to `submission.jsonl` in the required JSONL format.
2. **Create README**:
   Write a `README.md` explaining the system design, prompting strategies, and takeaways from the challenge.
