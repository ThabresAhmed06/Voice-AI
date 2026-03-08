import json
import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MANDATORY_FIELDS = ["equipment", "location_or_unit", "incident_summary"]


# ---------------- SAFE JSON ----------------

def safe_json(text):

    try:
        return json.loads(text)

    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {}


# ---------------- TEXT NORMALIZATION ----------------

def normalize_incident(text):

    if not text:
        return text

    text = text.lower()

    if "overheat" in text:
        return "overheating"

    if "leak" in text:
        return "leakage"

    if "malfunction" in text:
        return "malfunction"

    return text


# ---------------- FAST RULE PARSER ----------------

def fast_rule_parser(text):
    text = text.lower()
    result = {}

    # ... (keep your existing reporter, department, and equipment logic) ...

    # ---------------- UPDATED SEVERITY LOGIC ----------------
    # High / Critical Keywords
    if any(word in text for word in ["critical", "emergency", "explosion", "danger", "smoke", "fire", "sparks", "injured"]):
        result["severity"] = "High"
    
    # Medium / Warning Keywords
    elif any(word in text for word in ["leak", "malfunction", "warning", "overheat", "urgent", "vibration"]):
        result["severity"] = "Medium"
    
    # Default / Low Keywords
    else:
        result["severity"] = "Low"

    # ... (keep your existing time logic) ...
    return result

    text = text.lower()

    result = {}

    # reporter
    name_match = re.search(r"(this is|i am|my name is)\s+([a-z]+)", text)
    if name_match:
        result["reporter_name"] = name_match.group(2)

    # department
    dept_match = re.search(r"from\s+([a-z]+)\s+department", text)
    if dept_match:
        result["department"] = dept_match.group(1)

    # equipment
    if "motor" in text:
        result["equipment"] = "motor"

    elif "pump" in text:
        result["equipment"] = "pump"

    elif "valve" in text:
        result["equipment"] = "valve"

    elif "compressor" in text:
        result["equipment"] = "compressor"

    # location
    unit_match = re.search(r"unit\s*\d+", text)

    if unit_match:
        result["location_or_unit"] = unit_match.group()

    # incident
    if "overheat" in text or "heat" in text:
        result["incident_summary"] = "overheating"

    elif "leak" in text:
        result["incident_summary"] = "leakage"

    elif "malfunction" in text:
        result["incident_summary"] = "malfunction"

    # severity
    if "critical" in text or "emergency" in text or "explosion" in text or "danger" in text:
        result["severity"] = "critical"
    elif "leak" in text or "malfunction" in text:
        result["severity"] = "high"
    elif "overheat" in text or "heat" in text:
        result["severity"] = "medium"
    else:
        result["severity"] = "low"

    # time
    time_match = re.search(r"\d+\s*(am|pm)", text)

    if time_match:
        result["incident_time"] = time_match.group()

    return result


# ---------------- LLM EXTRACTION ----------------

def llm_extract(transcript):

    prompt = f"""
Extract incident report information as JSON.

Fields:
reporter_name
department
equipment
incident_summary
location_or_unit
incident_date
incident_time
severity
measured_parameters
remarks

Text:
{transcript}
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt,
        temperature=0,
        max_output_tokens=120
    )

    raw = response.output_text.strip()

    data = safe_json(raw)

    return data


# ---------------- MAIN EXTRACTION ----------------

def extract_structured_data(transcript):
    transcript = transcript.lower()

    # 1️⃣ Fast rule parser
    rule_data = fast_rule_parser(transcript)

    # if mandatory fields found → skip LLM
    if all(field in rule_data for field in MANDATORY_FIELDS):
        result = {
            "reporter_name": rule_data.get("reporter_name", ""),
            "department": rule_data.get("department", ""),
            "equipment": rule_data.get("equipment", ""),
            "incident_summary": normalize_incident(rule_data.get("incident_summary", "")),
            "location_or_unit": rule_data.get("location_or_unit", ""),
            "incident_date": "",
            "incident_time": rule_data.get("incident_time", ""),
            "severity": rule_data.get("severity", "Low"), # <--- CHANGED FROM "" TO rule_data
            "measured_parameters": "",
            "remarks": ""
        }
        return result

    # 2️⃣ otherwise use LLM
    data = llm_extract(transcript)
    
    # ... (rest of your logic for LLM fallback) ...
    
    # Ensure severity is normalized even in LLM results
    if result["severity"].lower() in ["critical", "high", "emergency"]:
        result["severity"] = "High"
    elif result["severity"].lower() in ["medium", "warning"]:
        result["severity"] = "Medium"
    else:
        result["severity"] = "Low"

    return result