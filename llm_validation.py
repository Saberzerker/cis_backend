
#! CURRENT STUB VALIDATOR
import re

def extract_control_headings_from_text(txt_path, lookahead_lines=6):
    """
    Returns a list of all control numbers and raw headings from a cleaned CIS .txt file,
    only after 'Recommendations', and only if a section header is found within next N lines.
    """
    section_headers = [
        "Profile Applicability", "Applicability", "Description", "Setting Description",
        "Rationale", "Rationale Statement", "Impact", "Impact Statement",
        "Audit", "Audit Procedure", "Audit Commands",
        "Remediation", "Remediation Procedure", "Remediation Commands",
        "Default Value", "Default value", "Default Configuration", "References", "Reference",
        "CIS Controls", "CIS Critical Security Controls", "CIS Control Mapping",
        "MITRE ATT&CK Mappings", "MITRE ATT&CK Mapping", "Additional Information"
    ]
    section_headers_lc = [h.lower() for h in section_headers]
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
    n = len(lines)
    # Find Recommendations
    rec_idx = -1
    for i, l in enumerate(lines):
        if l.strip().lower().startswith("recommendations"):
            rec_idx = i
            break
    if rec_idx == -1:
        rec_idx = 0
    lines = lines[rec_idx:]
    headings = []
    i = 0
    control_header_regex = re.compile(r"^((\d+\.)+\d+)\s+(.+)")
    while i < len(lines):
        match = control_header_regex.match(lines[i])
        if match:
            found_header = False
            for j in range(1, lookahead_lines+1):
                if i + j >= len(lines): break
                l2 = lines[i+j].strip().lower().rstrip(':')
                if l2 in section_headers_lc:
                    found_header = True
                    break
            if found_header:
                headings.append((match.group(1), match.group(3)))
            i += 1
            continue
        match2 = re.match(r"^((\d+\.)+\d+)\s*$", lines[i])
        if match2 and i+1 < len(lines):
            found_header = False
            for j in range(1, lookahead_lines+2):
                if i + j >= len(lines): break
                l2 = lines[i+j].strip().lower().rstrip(':')
                if l2 in section_headers_lc:
                    found_header = True
                    break
            if found_header:
                headings.append((match2.group(1), lines[i+1].strip()))
            i += 2
            continue
        i += 1
    return headings

def llm_cross_validate(parsed, txt_path):
    """
    Validator that:
    - Parses cleaned text for all control headings (using regex, with lookahead)
    - Counts expected controls (only after Recommendations, only with section header)
    - Compares to parser output (IDs)
    - Lists missing controls (IDs/titles)
    """
    expected = extract_control_headings_from_text(txt_path)
    expected_ids = set(e[0] for e in expected)
    expected_details = {e[0]: e[1] for e in expected}

    found_ids = set()
    found_titles = {}
    for ctrl in parsed:
        id_ = ctrl.get('ID', '').strip()
        title = ctrl.get('Title', '').strip()
        if id_:
            found_ids.add(id_)
            found_titles[id_] = title

    missing = sorted(list(expected_ids - found_ids))
    extra = sorted(list(found_ids - expected_ids))
    matched = sorted(list(expected_ids & found_ids))
    percent = 0.0 if not expected_ids else 100 * len(matched) / len(expected_ids)
    status = "ok" if percent >= 95.0 else "fail"
    summary = f"{percent:.1f}% of expected controls found ({len(matched)}/{len(expected_ids)})"

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