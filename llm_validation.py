import os
import json
import google.generativeai as genai

# Set your Gemini API key as an environment variable or load from .env
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise RuntimeError("Gemini API key not set. Please set GEMINI_API_KEY environment variable.")

MODEL = "models/gemini-1.5-pro-latest"  # adjust as needed

def llm_cross_validate(parsed, txt_path):
    """
    Uses Gemini LLM to validate parsed JSON against the cleaned text corpus.
    Returns a dict: {'status': 'ok'/'fail', 'summary': '...', 'recommendations': [ ... ]}
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        text_corpus = f.read()
    
    prompt = (
        "You are a compliance document QA assistant. "
        "Below is a text corpus extracted from a CIS Benchmark PDF, "
        "and a parsed JSON representing extracted controls. "
        "Compare the JSON to the text, flag any discrepancies (missing fields, mismatches, etc.) "
        "and suggest corrections. List each issue as: "
        "[ID] | [Fault Type] | [Description] | [Recommended Fix]. "
        "Return a JSON array of recommendations. If all good, reply: 'No discrepancies found.'\n\n"
        f"Text Corpus:\n{text_corpus[:4000]}...\n\n"  # Limit to first 4000 chars for context
        f"Parsed JSON:\n{json.dumps(parsed)[:4000]}...\n"  # Limit for context
    )

    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)
    content = response.text.strip()

    # Try to parse recommendations out of response
    recommendations = []
    status = "ok"
    summary = "All fields present and correct."
    if "No discrepancies" not in content:
        try:
            # Try to parse JSON array from LLM response
            recommendations = json.loads(content.split("\n", 1)[-1])
            status = "fail"
            summary = f"{len(recommendations)} discrepancies found."
        except Exception:
            # Fallback: treat each line as a recommendation
            lines = [line for line in content.splitlines() if "|" in line]
            for line in lines:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 4:
                    recommendations.append({
                        "id": parts[0],
                        "fault_type": parts[1],
                        "description": parts[2],
                        "fix": parts[3]
                    })
            if recommendations:
                status = "fail"
                summary = f"{len(recommendations)} discrepancies found."
            else:
                summary = f"LLM output not parseable: {content}"
                status = "fail"

    return {
        "status": status,
        "summary": summary,
        "recommendations": recommendations,
        "raw_output": content
    }