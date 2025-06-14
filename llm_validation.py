# import os
# import json
# import google.generativeai as genai

# # Set your Gemini API key as an environment variable or load from .env
# API_KEY = os.getenv("GEMINI_API_KEY")

# if API_KEY:
#     genai.configure(api_key=API_KEY)
# else:
#     raise RuntimeError("Gemini API key not set. Please set GEMINI_API_KEY environment variable.")

# MODEL = "models/gemini-1.5-pro-latest"  # adjust as needed

# def llm_cross_validate(parsed, txt_path):
#     """
#     Uses Gemini LLM to validate parsed JSON against the cleaned text corpus.
#     Returns a dict: {'status': 'ok'/'fail', 'summary': '...', 'recommendations': [ ... ]}
#     """
#     with open(txt_path, "r", encoding="utf-8") as f:
#         text_corpus = f.read()
    
#     prompt = (
#         "You are a compliance document QA assistant. "
#         "Below is a text corpus extracted from a CIS Benchmark PDF, "
#         "and a parsed JSON representing extracted controls. "
#         "Compare the JSON to the text, flag any discrepancies (missing fields, mismatches, etc.) "
#         "and suggest corrections. List each issue as: "
#         "[ID] | [Fault Type] | [Description] | [Recommended Fix]. "
#         "Return a JSON array of recommendations. If all good, reply: 'No discrepancies found.'\n\n"
#         f"Text Corpus:\n{text_corpus[:4000]}...\n\n"  # Limit to first 4000 chars for context
#         f"Parsed JSON:\n{json.dumps(parsed)[:4000]}...\n"  # Limit for context
#     )

#     model = genai.GenerativeModel(MODEL)
#     response = model.generate_content(prompt)
#     content = response.text.strip()

#     # Try to parse recommendations out of response
#     recommendations = []
#     status = "ok"
#     summary = "All fields present and correct."
#     if "No discrepancies" not in content:
#         try:
#             # Try to parse JSON array from LLM response
#             recommendations = json.loads(content.split("\n", 1)[-1])
#             status = "fail"
#             summary = f"{len(recommendations)} discrepancies found."
#         except Exception:
#             # Fallback: treat each line as a recommendation
#             lines = [line for line in content.splitlines() if "|" in line]
#             for line in lines:
#                 parts = [p.strip() for p in line.split("|")]
#                 if len(parts) == 4:
#                     recommendations.append({
#                         "id": parts[0],
#                         "fault_type": parts[1],
#                         "description": parts[2],
#                         "fix": parts[3]
#                     })
#             if recommendations:
#                 status = "fail"
#                 summary = f"{len(recommendations)} discrepancies found."
#             else:
#                 summary = f"LLM output not parseable: {content}"
#                 status = "fail"

#     return {
#         "status": status,
#         "summary": summary,
#         "recommendations": recommendations,
#         "raw_output": content
#     }




# import json

# def llm_cross_validate(parsed, txt_path):
#     """
#     Stub for LLM validation (no real Gemini/AI calls).
#     Returns a dict: {'status': 'ok'/'fail', 'summary': '...', 'recommendations': [ ... ]}
#     """
#     # For now, always pass if >90% controls have 'ID' and 'Description'
#     missing = 0
#     total = len(parsed)
#     for x in parsed:
#         if not x.get('ID') or not x.get('Description'):
#             missing += 1
#     if total == 0 or missing / total > 0.1:
#         return {
#             "status": "fail",
#             "summary": f"{missing} controls missing critical fields.",
#             "recommendations": [
#                 {"id": x.get("ID", "?"), "fault_type": "Missing Field", "description": "ID or Description missing", "fix": "Check parsing logic."}
#                 for x in parsed if not x.get("ID") or not x.get("Description")
#             ],
#             "raw_output": "Stub: Some controls missing fields."
#         }
#     else:
#         return {
#             "status": "ok",
#             "summary": "All fields present and correct.",
#             "recommendations": [],
#             "raw_output": "Stub: No discrepancies found."
#         }


#? New and improved

import re
import json

def extract_control_headings_from_text(txt_path):
    """
    Returns a list of all control numbers and raw headings from a cleaned CIS .txt file.
    Handles controls like: 1.2.1 Ensure X, or multi-line headings ("1.2.1" + "Ensure X" on next line).
    """
    headings = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
    n = len(lines)
    i = 0
    while i < n:
        # Case 1: Number and title on same line
        match = re.match(r"^((\d+\.)+\d+)\s+(.+)", lines[i])
        if match:
            headings.append((match.group(1), match.group(3)))
            i += 1
            continue
        # Case 2: Number on its own line, title on next line
        match = re.match(r"^((\d+\.)+\d+)\s*$", lines[i])
        if match and i+1 < n and lines[i+1].strip():
            headings.append((match.group(1), lines[i+1].strip()))
            i += 2
            continue
        i += 1
    return headings

def llm_cross_validate(parsed, txt_path):
    """
    Validator that:
    - Parses cleaned text for all control headings (using regex)
    - Counts expected controls
    - Compares to parser output (IDs)
    - Lists missing controls (IDs/titles)
    """
    # Step 1: Extract headings from cleaned text
    expected = extract_control_headings_from_text(txt_path)
    expected_ids = set(e[0] for e in expected)
    expected_details = {e[0]: e[1] for e in expected}

    # Step 2: Get actual IDs from parsed JSON (list of dicts)
    found_ids = set()
    found_titles = {}
    for ctrl in parsed:
        id_ = ctrl.get('ID', '').strip()
        title = ctrl.get('Title', '').strip()
        if id_:
            found_ids.add(id_)
            found_titles[id_] = title

    # Step 3: Compare and report
    missing = sorted(list(expected_ids - found_ids))
    extra = sorted(list(found_ids - expected_ids))
    matched = sorted(list(expected_ids & found_ids))
    percent = 0.0 if not expected_ids else 100 * len(matched) / len(expected_ids)
    status = "ok" if percent >= 95.0 else "fail"
    summary = f"{percent:.1f}% of expected controls found ({len(matched)}/{len(expected_ids)})"

    # List titles for missing controls
    missing_titles = [(mid, expected_details[mid]) for mid in missing]

    result = {
        "status": status,
        "summary": summary,
        "expected_controls": len(expected_ids),
        "found_controls": len(found_ids),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "percent_found": percent,
        "missing_controls": missing_titles,
        "extra_controls": extra,
        "matched_controls": matched
    }
    return result

