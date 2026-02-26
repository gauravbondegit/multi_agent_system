import google.generativeai as genai
import os
import json
import datetime
from dotenv import load_dotenv
import re

load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-2.5-flash') 

CONTROLLER_LOG_FILE = "logs/controller_log.jsonl"
ALLOWED_AGENTS = {"PDF_RAG_AGENT", "WEB_SEARCH_AGENT", "ARXIV_AGENT"}

def get_controller_prompt(query: str, pdf_uploaded: bool):
    """Generates the prompt for the controller LLM."""
    
    prompt = f"""
    You are an expert AI system controller. Your job is to analyze the user's query and decide which agent(s) to call to best answer it. You must respond ONLY with a valid JSON object and nothing else.

    Available Agents:
    1. "PDF_RAG_AGENT": Use for questions specifically about an uploaded document's content.
    2. "WEB_SEARCH_AGENT": Use for general knowledge, news, recent events, or any query that is not clearly about a PDF or academic research.
    3. "ARXIV_AGENT": Use for queries about scientific papers, research, studies, technical topics, or academic articles.

    User Query: "{query}"
    PDF Uploaded: {pdf_uploaded}

    Decision Logic:
    - Analyze the user's intent. The presence of words like "paper," "papers," "study," "research," or "arxiv" strongly suggests using "ARXIV_AGENT".
    - If a PDF is uploaded and the query mentions "this document," "the PDF," or similar, you MUST use "PDF_RAG_AGENT".
    - If the intent is unclear or it's a general knowledge question, default to "WEB_SEARCH_AGENT".

    Example for a tricky query:
    User Query: "latest papers on AI ethics"
    Correct Decision: {{ "reasoning": "The user is asking for 'papers,' which indicates a request for academic research. The ArXiv agent is the best tool for this.", "agents": ["ARXIV_AGENT"] }}

    Provide your decision as a JSON object with two keys: "reasoning" and "agents".
    """
    return prompt

def extract_json_from_string(text: str):
    """Extracts the first valid JSON object from free-form model text."""
    if not text:
        return None

    fenced_json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    candidates = []
    if fenced_json_match:
        candidates.append(fenced_json_match.group(1))
    candidates.append(text)

    decoder = json.JSONDecoder()
    for candidate in candidates:
        idx = 0
        while idx < len(candidate):
            start = candidate.find("{", idx)
            if start == -1:
                break
            try:
                parsed_obj, end = decoder.raw_decode(candidate[start:])
                if isinstance(parsed_obj, dict):
                    return parsed_obj
                idx = start + end
            except json.JSONDecodeError:
                idx = start + 1
    return None

def normalize_decision(decision_json: dict):
    """Normalizes and validates controller JSON to expected schema."""
    if not isinstance(decision_json, dict):
        return None

    reasoning = decision_json.get("reasoning", "No reasoning provided.")
    agents = decision_json.get("agents", [])
    if isinstance(agents, str):
        agents = [agents]
    if not isinstance(agents, list):
        agents = []

    filtered_agents = [agent for agent in agents if agent in ALLOWED_AGENTS]
    if not filtered_agents:
        filtered_agents = ["WEB_SEARCH_AGENT"]

    return {
        "reasoning": str(reasoning),
        "agents": filtered_agents,
    }

def decide_route(query: str, pdf_uploaded: bool):
    """Uses the LLM to decide which agent(s) to call."""
    prompt = get_controller_prompt(query, pdf_uploaded)
    
    try:
        response = model.generate_content(prompt)
        
        # Use the robust JSON extraction function
        decision_json = extract_json_from_string(response.text)
        decision_json = normalize_decision(decision_json)
        
        if not decision_json:
            # This will be triggered if JSON is still not found or is malformed
            raise ValueError(f"Could not parse JSON from LLM response: {response.text}")

        log_decision(query, decision_json)
        return decision_json
        
    except Exception as e:
        print(f"Error in controller decision: {e}")
        # Fallback logic
        fallback_decision = {
            "reasoning": f"Controller LLM failed. Reason: {e}", # Log the actual error
            "agents": ["WEB_SEARCH_AGENT"]
        }
        log_decision(query, fallback_decision)
        return fallback_decision

def log_decision(query, decision):
    """Logs the controller's decision to a file."""
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "query": query,
        "decision": decision
    }
    os.makedirs(os.path.dirname(CONTROLLER_LOG_FILE), exist_ok=True)
    with open(CONTROLLER_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")