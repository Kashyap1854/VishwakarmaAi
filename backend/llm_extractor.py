"""
llm_extractor.py — Extract structured monument info via Ollama/Mistral
Falls back to empty dict if Ollama is not running.
"""
import json

def extract_details_llm(summary: str) -> dict:
    try:
        import ollama
        prompt = f"""You are an AI that extracts structured information about monuments.

Extract ONLY these fields:
- Architecture
- Built (year or period)
- Builder (person or dynasty)
- Location

Rules:
- Use only the given text
- Do NOT guess
- If missing → "Not available"
- Return ONLY valid JSON, no extra text

Text:
{summary}"""

        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response["message"]["content"].strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return {}
