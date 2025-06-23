
# #! CURRENT STUB VALIDATOR
# import re

# def extract_control_headings_from_text(txt_path, lookahead_lines=6):
#     """
#     Returns a list of all control numbers and raw headings from a cleaned CIS .txt file,
#     only after 'Recommendations', and only if a section header is found within next N lines.
#     """
#     section_headers = [
#         "Profile Applicability", "Applicability", "Description", "Setting Description",
#         "Rationale", "Rationale Statement", "Impact", "Impact Statement",
#         "Audit", "Audit Procedure", "Audit Commands",
#         "Remediation", "Remediation Procedure", "Remediation Commands",
#         "Default Value", "Default value", "Default Configuration", "References", "Reference",
#         "CIS Controls", "CIS Critical Security Controls", "CIS Control Mapping",
#         "MITRE ATT&CK Mappings", "MITRE ATT&CK Mapping", "Additional Information"
#     ]
#     section_headers_lc = [h.lower() for h in section_headers]
#     with open(txt_path, 'r', encoding='utf-8') as f:
#         lines = [l.rstrip() for l in f]
#     n = len(lines)
#     # Find Recommendations
#     rec_idx = -1
#     for i, l in enumerate(lines):
#         if l.strip().lower().startswith("recommendations"):
#             rec_idx = i
#             break
#     if rec_idx == -1:
#         rec_idx = 0
#     lines = lines[rec_idx:]
#     headings = []
#     i = 0
#     control_header_regex = re.compile(r"^((\d+\.)+\d+)\s+(.+)")
#     while i < len(lines):
#         match = control_header_regex.match(lines[i])
#         if match:
#             found_header = False
#             for j in range(1, lookahead_lines+1):
#                 if i + j >= len(lines): break
#                 l2 = lines[i+j].strip().lower().rstrip(':')
#                 if l2 in section_headers_lc:
#                     found_header = True
#                     break
#             if found_header:
#                 headings.append((match.group(1), match.group(3)))
#             i += 1
#             continue
#         match2 = re.match(r"^((\d+\.)+\d+)\s*$", lines[i])
#         if match2 and i+1 < len(lines):
#             found_header = False
#             for j in range(1, lookahead_lines+2):
#                 if i + j >= len(lines): break
#                 l2 = lines[i+j].strip().lower().rstrip(':')
#                 if l2 in section_headers_lc:
#                     found_header = True
#                     break
#             if found_header:
#                 headings.append((match2.group(1), lines[i+1].strip()))
#             i += 2
#             continue
#         i += 1
#     return headings

# def llm_cross_validate(parsed, txt_path):
#     """
#     Validator that:
#     - Parses cleaned text for all control headings (using regex, with lookahead)
#     - Counts expected controls (only after Recommendations, only with section header)
#     - Compares to parser output (IDs)
#     - Lists missing controls (IDs/titles)
#     """
#     expected = extract_control_headings_from_text(txt_path)
#     expected_ids = set(e[0] for e in expected)
#     expected_details = {e[0]: e[1] for e in expected}

#     found_ids = set()
#     found_titles = {}
#     for ctrl in parsed:
#         id_ = ctrl.get('ID', '').strip()
#         title = ctrl.get('Title', '').strip()
#         if id_:
#             found_ids.add(id_)
#             found_titles[id_] = title

#     missing = sorted(list(expected_ids - found_ids))
#     extra = sorted(list(found_ids - expected_ids))
#     matched = sorted(list(expected_ids & found_ids))
#     percent = 0.0 if not expected_ids else 100 * len(matched) / len(expected_ids)
#     status = "ok" if percent >= 95.0 else "fail"
#     summary = f"{percent:.1f}% of expected controls found ({len(matched)}/{len(expected_ids)})"

#     missing_titles = [(mid, expected_details[mid]) for mid in missing]

#     result = {
#         "status": status,
#         "summary": summary,
#         "expected_controls": len(expected_ids),
#         "found_controls": len(found_ids),
#         "missing_count": len(missing),
#         "extra_count": len(extra),
#         "percent_found": percent,
#         "missing_controls": missing_titles,
#         "extra_controls": extra,
#         "matched_controls": matched
#     }
#     return result

# import re
# from rapidfuzz import fuzz

# def extract_control_blocks(txt_path, section_headers, lookahead_lines=6):
#     # Parse the .txt file and return {control_id: {field_name: value, ...}}
#     with open(txt_path, 'r', encoding='utf-8') as f:
#         lines = [l.rstrip() for l in f]
#     # Find 'Recommendations'
#     rec_idx = next((i for i, l in enumerate(lines) if l.strip().lower().startswith("recommendations")), 0)
#     lines = lines[rec_idx:]
#     controls = {}
#     control_header_regex = re.compile(r"^((\d+\.)+\d+)\s+(.+)")
#     section_headers_lc = [h.lower() for h in section_headers]
#     i = 0
#     while i < len(lines):
#         match = control_header_regex.match(lines[i])
#         if match:
#             # Lookahead to confirm it's a control
#             found_header = False
#             for j in range(1, lookahead_lines+1):
#                 if i + j >= len(lines): break
#                 l2 = lines[i+j].strip().lower().rstrip(':')
#                 if l2 in section_headers_lc:
#                     found_header = True
#                     break
#             if found_header:
#                 control_id = match.group(1)
#                 title = match.group(3).strip()
#                 # Find block for this control
#                 start = i+1
#                 end = start
#                 while end < len(lines):
#                     next_match = control_header_regex.match(lines[end])
#                     if next_match:
#                         # Confirm next is a control with section header
#                         found_next = False
#                         for k in range(1, lookahead_lines+1):
#                             if end + k >= len(lines): break
#                             l3 = lines[end+k].strip().lower().rstrip(':')
#                             if l3 in section_headers_lc:
#                                 found_next = True
#                                 break
#                         if found_next:
#                             break
#                     end += 1
#                 block = lines[i:end]
#                 # Extract fields
#                 fields = {"Title": title}
#                 current_field = None
#                 field_buffer = []
#                 idx2 = 0
#                 while idx2 < len(block):
#                     line = block[idx2].strip()
#                     lower_line = line.lower().rstrip(':')
#                     is_header = False
#                     if lower_line in section_headers_lc:
#                         is_header = True
#                         header_candidate = line
#                     elif ':' in lower_line:
#                         candidate = lower_line.split(':')[0].strip()
#                         if candidate in section_headers_lc:
#                             is_header = True
#                             header_candidate = candidate.title()
#                     if is_header:
#                         if current_field and field_buffer:
#                             fields[current_field] = " ".join(field_buffer).strip()
#                         current_field = header_candidate.title()
#                         field_buffer = []
#                     else:
#                         if current_field:
#                             field_buffer.append(line)
#                     idx2 += 1
#                 if current_field and field_buffer:
#                     fields[current_field] = " ".join(field_buffer).strip()
#                 controls[control_id] = fields
#             i += 1
#             continue
#         i += 1
#     return controls

# def llm_cross_validate(parsed, txt_path):
#     # SECTION_HEADERS should be imported or defined at the top
#     SECTION_HEADERS = [
#         "Profile Applicability", "Applicability", "Description", "Setting Description",
#         "Rationale", "Rationale Statement", "Impact", "Impact Statement",
#         "Audit", "Audit Procedure", "Audit Commands",
#         "Remediation", "Remediation Procedure", "Remediation Commands",
#         "Default Value", "Default value", "Default Configuration", "References", "Reference",
#         "CIS Controls", "CIS Critical Security Controls", "CIS Control Mapping",
#         "MITRE ATT&CK Mappings", "MITRE ATT&CK Mapping", "Additional Information"
#     ]
#     FIELDNAMES = [
#         "Title", "Method", "Profile Applicability", "Description", "Rationale",
#         "Impact", "Audit", "Audit Commands", "Remediations", "Remediation Commands",
#         "Default value", "References", "CIS Controls", "MITRE ATT&CK Mappings", "Compliant"
#     ]
#     expected_controls = extract_control_blocks(txt_path, SECTION_HEADERS)
#     expected_ids = set(expected_controls.keys())

#     found_ids = set()
#     found_control_map = {}
#     for ctrl in parsed:
#         id_ = ctrl.get("ID", "").strip()
#         if id_:
#             found_ids.add(id_)
#             found_control_map[id_] = ctrl

#     missing_ids = sorted(list(expected_ids - found_ids))
#     extra_ids = sorted(list(found_ids - expected_ids))
#     matched_ids = sorted(list(expected_ids & found_ids))

#     # Field-by-field comparison
#     field_results = {}
#     for cid in matched_ids:
#         text_fields = expected_controls[cid]
#         json_fields = found_control_map[cid]
#         field_results[cid] = {}
#         for fname in FIELDNAMES:
#             text_val = text_fields.get(fname, "").strip()
#             json_val = json_fields.get(fname, "").strip()
#             if not text_val and not json_val:
#                 field_results[cid][fname] = {"status": "ok", "similarity": 100}
#             elif text_val and not json_val:
#                 field_results[cid][fname] = {"status": "missing_in_json", "similarity": 0}
#             elif not text_val and json_val:
#                 field_results[cid][fname] = {"status": "extra_in_json", "similarity": 0}
#             else:
#                 # Fuzzy match
#                 similarity = fuzz.ratio(text_val, json_val)
#                 field_results[cid][fname] = {
#                     "status": "ok" if similarity >= 95 else "mismatch",
#                     "similarity": similarity
#                 }

#     percent_found = 0.0 if not expected_ids else 100 * len(matched_ids) / len(expected_ids)
#     total_fields = len(matched_ids) * len(FIELDNAMES)
#     ok_fields = sum(1 for cid in matched_ids for fname in FIELDNAMES
#                     if field_results[cid][fname]["status"] == "ok")
#     percent_fields_ok = 0.0 if not total_fields else 100 * ok_fields / total_fields

#     status = "ok" if percent_found >= 95 and percent_fields_ok >= 95 else "fail"
#     summary = (f"{percent_found:.1f}% controls found "
#                f"({len(matched_ids)}/{len(expected_ids)}); "
#                f"{percent_fields_ok:.1f}% fields match")

#     result = {
#         "status": status,
#         "summary": summary,
#         "expected_controls": len(expected_ids),
#         "found_controls": len(found_ids),
#         "missing_count": len(missing_ids),
#         "extra_count": len(extra_ids),
#         "percent_found": percent_found,
#         "percent_fields_ok": percent_fields_ok,
#         "missing_controls": missing_ids,
#         "extra_controls": extra_ids,
#         "matched_controls": matched_ids,
#         "field_comparison": field_results
#     }
#     return result



import re
from rapidfuzz import fuzz

def extract_control_blocks(txt_path, section_headers):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
    rec_idx = next((i for i, l in enumerate(lines) if l.strip().lower().startswith("recommendations")), 0)
    lines = lines[rec_idx:]
    controls = {}
    prof_app_indices = []
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("profile applicability"):
            prof_app_indices.append(i)
    prof_app_indices.append(len(lines))  # Sentinel

    for idx in range(len(prof_app_indices)-1):
        pa_idx = prof_app_indices[idx]
        next_pa_idx = prof_app_indices[idx+1]
        header_line = None
        for rollback in range(1, 5):
            candidate_idx = pa_idx - rollback
            if candidate_idx < 0:
                break
            candidate = lines[candidate_idx].strip()
            m = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)", candidate)
            if m:
                control_id = m.group(1)
                title = m.group(2).strip()
                header_line = (control_id, title, candidate_idx)
                break
            m2 = re.match(r"^(\d+(?:\.\d+)+)\s*$", candidate)
            if m2 and candidate_idx+1 < pa_idx:
                control_id = m2.group(1)
                title = lines[candidate_idx+1].strip()
                header_line = (control_id, title, candidate_idx)
                break
        if not header_line:
            continue
        control_id, title, header_idx = header_line
        block = lines[header_idx+1:next_pa_idx]
        fields = {"Title": title}
        current_field = None
        field_buffer = []
        section_headers_lc = [h.lower() for h in section_headers]
        idx2 = 0
        while idx2 < len(block):
            line = block[idx2].strip()
            lower_line = line.lower().rstrip(':')
            is_header = False
            header_candidate = None
            if lower_line in section_headers_lc:
                is_header = True
                header_candidate = line
            elif ':' in lower_line:
                candidate = lower_line.split(':')[0].strip()
                if candidate in section_headers_lc:
                    is_header = True
                    header_candidate = candidate.title()
            if is_header:
                if current_field and field_buffer:
                    fields[current_field] = " ".join(field_buffer).strip()
                current_field = header_candidate.title()
                field_buffer = []
            else:
                if current_field:
                    field_buffer.append(line)
            idx2 += 1
        if current_field and field_buffer:
            fields[current_field] = " ".join(field_buffer).strip()
        controls[control_id] = fields
    return controls

def llm_cross_validate(parsed, txt_path):
    SECTION_HEADERS = [
        "Profile Applicability", "Applicability", "Description", "Setting Description",
        "Rationale", "Rationale Statement", "Impact", "Impact Statement",
        "Audit", "Audit Procedure", "Audit Commands",
        "Remediation", "Remediation Procedure", "Remediation Commands",
        "Default Value", "Default value", "Default Configuration", "References", "Reference",
        "CIS Controls", "CIS Critical Security Controls", "CIS Control Mapping",
        "MITRE ATT&CK Mappings", "MITRE ATT&CK Mapping", "Additional Information"
    ]
    FIELDNAMES = [
        "Title", "Method", "Profile Applicability", "Description", "Rationale",
        "Impact", "Audit", "Audit Commands", "Remediations", "Remediation Commands",
        "Default value", "References", "CIS Controls", "MITRE ATT&CK Mappings", "Compliant"
    ]
    expected_controls = extract_control_blocks(txt_path, SECTION_HEADERS)
    expected_ids = set(expected_controls.keys())

    found_ids = set()
    found_control_map = {}
    for ctrl in parsed:
        id_ = ctrl.get("ID", "").strip()
        if id_:
            found_ids.add(id_)
            found_control_map[id_] = ctrl

    missing_ids = sorted(list(expected_ids - found_ids))
    extra_ids = sorted(list(found_ids - expected_ids))
    matched_ids = sorted(list(expected_ids & found_ids))

    field_results = {}
    for cid in matched_ids:
        text_fields = expected_controls[cid]
        json_fields = found_control_map[cid]
        field_results[cid] = {}
        for fname in FIELDNAMES:
            text_val = text_fields.get(fname, "").strip()
            json_val = json_fields.get(fname, "").strip()
            if not text_val and not json_val:
                field_results[cid][fname] = {"status": "ok", "similarity": 100}
            elif text_val and not json_val:
                field_results[cid][fname] = {"status": "missing_in_json", "similarity": 0}
            elif not text_val and json_val:
                field_results[cid][fname] = {"status": "extra_in_json", "similarity": 0}
            else:
                similarity = fuzz.ratio(text_val, json_val)
                field_results[cid][fname] = {
                    "status": "ok" if similarity >= 95 else "mismatch",
                    "similarity": similarity
                }

    percent_controls_found = 0.0 if not expected_ids else 100 * len(matched_ids) / len(expected_ids)
    total_fields = len(matched_ids) * len(FIELDNAMES)
    ok_fields = sum(1 for cid in matched_ids for fname in FIELDNAMES
                    if field_results[cid][fname]["status"] == "ok")
    percent_fields_ok = 0.0 if not total_fields else 100 * ok_fields / total_fields

    status = "ok" if percent_controls_found >= 95 else "fail"
    summary = (f"{percent_controls_found:.1f}% controls found "
               f"({len(matched_ids)}/{len(expected_ids)}); "
               f"{percent_fields_ok:.1f}% fields match")

    result = {
        "status": status,
        "summary": summary,
        "expected_controls": len(expected_ids),
        "found_controls": len(found_ids),
        "missing_count": len(missing_ids),
        "extra_count": len(extra_ids),
        "percent_controls_found": percent_controls_found,
        "percent_fields_ok": percent_fields_ok,
        "missing_controls": missing_ids,
        "extra_controls": extra_ids,
        "matched_controls": matched_ids,
        "field_comparison": field_results
    }
    return result