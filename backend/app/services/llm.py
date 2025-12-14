from ..config import LLM_PROVIDER, GOOGLE_API_KEY, GEMINI_LLM_MODEL
import json


# Lazy initialization - Gemini only
def _get_genai_client():
    """Lazy initialization of Gemini client"""
    if LLM_PROVIDER == "gemini" and GOOGLE_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GOOGLE_API_KEY)
            return client
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            return None
    return None

def classify_control_with_gemini(control_id, control_text, evidences, max_output_tokens=2048, temperature=0.0):
    # Gemini models don't use separate system prompts - include instructions in the main prompt
    evidence_text = ""
    for i, e in enumerate(evidences, start=1):
        snippet = e.get("snippet","").replace("\n"," ").strip()
        if snippet:
            evidence_text += f"{i}) Document: {e.get('doc_id', 'unknown')}, Page: {e.get('page', 'unknown')}\n   Text: \"{snippet}\"\n\n"

    prompt = (
        "Analyze evidence to classify a security control as Covered, Partial, or Missing.\n\n"
        "Classification Rules:\n"
        "- Covered: Evidence clearly shows the control is fully implemented as described\n"
        "- Partial: Evidence shows some implementation but incomplete, unclear, or partially meets requirements\n"
        "- Missing: No relevant evidence found, or evidence explicitly states the control is missing/non-compliant\n\n"
        "Important:\n"
        "- Look for related terms and concepts, not just exact matches\n"
        "- Consider synonyms and related security practices\n"
        "- If evidence mentions the concept but with different wording, it may still be Covered or Partial\n"
        "- Be lenient with terminology - vendors may use different terms for the same concept\n"
        "- Use ONLY provided evidence, but interpret it intelligently\n\n"
        f"Control ID: {control_id}\n"
        f"Control Name: {control_text}\n\n"
        f"Evidence Items:\n{evidence_text if evidence_text else 'No evidence provided.'}\n\n"
        "Return JSON only (no markdown):\n"
        '{"control_id":"' + control_id + '","classification":"Covered|Partial|Missing","confidence":0.0-1.0,"rationale":"detailed explanation citing specific evidence","followup_questions":["q1","q2"]}'
    )

    client = _get_genai_client()
    if client is None:
        return {
            "control_id": control_id,
            "classification": "Missing",
            "confidence": 0.0,
            "rationale": "LLM provider not configured (missing Google API key).",
            "evidence": evidences,
            "followup_questions": []
        }

    try:
        from google.genai import types
        resp = client.models.generate_content(
            model=GEMINI_LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        )
        text = resp.text
    except Exception as e:
        return {
            "control_id": control_id,
            "classification": "Missing",
            "confidence": 0.0,
            "rationale": f"LLM call failed: {str(e)}",
            "evidence": evidences,
            "followup_questions": []
        }

    if not text:
        return {
            "control_id": control_id,
            "classification": "Missing",
            "confidence": 0.0,
            "rationale": "Empty LLM response",
            "evidence": evidences,
            "followup_questions": []
        }

    # Clean the text - remove markdown code blocks if present
    cleaned_text = text.strip()
    
    # Remove markdown code block markers (```json ... ``` or ``` ... ```)
    if cleaned_text.startswith("```"):
        first_newline = cleaned_text.find("\n")
        if first_newline != -1:
            cleaned_text = cleaned_text[first_newline + 1:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
    
    # Try parsing JSON directly first
    try:
        parsed = json.loads(cleaned_text)
        return _validate_parsed_response(parsed, control_id, evidences)
    except json.JSONDecodeError:
        pass
    
    # If direct parsing fails, try to extract and fix incomplete JSON
    import re
    
    # Find the JSON object start
    json_start = cleaned_text.find('{')
    if json_start == -1:
        return _create_error_response(control_id, text, evidences, "No JSON object found")
    
    # Extract from first { to end, then try to complete it
    json_candidate = cleaned_text[json_start:]
    
    # Try to find complete JSON by matching braces
    brace_count = 0
    end_pos = -1
    in_string = False
    escape_next = False
    
    for i, char in enumerate(json_candidate):
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    if end_pos > 0:
        try:
            complete_json = json_candidate[:end_pos]
            parsed = json.loads(complete_json)
            return _validate_parsed_response(parsed, control_id, evidences)
        except json.JSONDecodeError:
            pass
    
    # If still failing, try to extract what we can and build a partial response
    # Extract classification if present
    classification_match = re.search(r'"classification"\s*:\s*"([^"]+)"', cleaned_text)
    confidence_match = re.search(r'"confidence"\s*:\s*([0-9.]+)', cleaned_text)
    rationale_match = re.search(r'"rationale"\s*:\s*"([^"]*)', cleaned_text)
    
    if classification_match:
        classification = classification_match.group(1)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5
        rationale = rationale_match.group(1) if rationale_match else "Response was truncated but classification found"
        if len(rationale) > 500:
            rationale = rationale[:500] + "..."
        
        return {
            "control_id": control_id,
            "classification": classification,
            "confidence": confidence,
            "rationale": rationale,
            "followup_questions": []
        }
    
    return _create_error_response(control_id, text, evidences, "Could not extract JSON")

def _validate_parsed_response(parsed, control_id, evidences):
    """Validate and fix parsed JSON response"""
    if "followup_questions" not in parsed:
        parsed["followup_questions"] = []
    elif not isinstance(parsed.get("followup_questions"), list):
        parsed["followup_questions"] = []
    
    # Ensure all required fields exist
    if "control_id" not in parsed:
        parsed["control_id"] = control_id
    if "classification" not in parsed:
        parsed["classification"] = "Missing"
    if "confidence" not in parsed:
        parsed["confidence"] = 0.0
    if "rationale" not in parsed:
        parsed["rationale"] = "No rationale provided"
    
    # Truncate rationale if too long
    if len(parsed.get("rationale", "")) > 1000:
        parsed["rationale"] = parsed["rationale"][:1000] + "..."
    
    return parsed

def _create_error_response(control_id, text, evidences, error_msg):
    """Create an error response"""
    return {
        "control_id": control_id,
        "classification": "Missing",
        "confidence": 0.0,
        "rationale": f"{error_msg}. Raw: {text[:300]}",
        "evidence": evidences,
        "followup_questions": []
    }
