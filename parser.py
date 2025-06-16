
#! FINAL VERSION OF THE PARSER WHICH WORKS AHH!!!
import re

def parse_text(txt_path):
    """
    Robust CIS Benchmark parser that only parses controls after 'Recommendations'
    and only includes a control if a section header (e.g. Profile Applicability) is found within the next 6 lines.
    """
    section_names = [
        "Profile Applicability", "Applicability", "Description", "Setting Description",
        "Rationale", "Rationale Statement", "Impact", "Impact Statement",
        "Audit", "Audit Procedure", "Audit Commands",
        "Remediation", "Remediation Procedure", "Remediation Commands",
        "Default Value", "Default value", "Default Configuration", "References", "Reference",
        "CIS Controls", "CIS Critical Security Controls", "CIS Control Mapping",
        "MITRE ATT&CK Mappings", "MITRE ATT&CK Mapping", "Additional Information"
    ]
    section_names_set = set([s.lower() for s in section_names])
    header_map = {
        "applicability": "Profile Applicability",
        "setting description": "Description",
        "rationale statement": "Rationale",
        "impact statement": "Impact",
        "audit procedure": "Audit",
        "remediation procedure": "Remediations",
        "default configuration": "Default value",
        "reference": "References",
        "cis critical security controls": "CIS Controls",
        "cis control mapping": "CIS Controls",
        "mitre att&ck mapping": "MITRE ATT&CK Mappings",
        "default value": "Default value",
    }

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [l.rstrip() for l in f]
    n = len(lines)

    # Find start of "Recommendations"
    rec_idx = -1
    for i, l in enumerate(lines):
        if l.strip().lower().startswith("recommendations"):
            rec_idx = i
            break
    if rec_idx == -1:
        print("Recommendations section not found, parsing entire file.")
        rec_idx = 0
    lines = lines[rec_idx:]

    controls = []
    i = 0
    control_header_regex = re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)")
    lookahead_lines = 6

    while i < len(lines):
        match = control_header_regex.match(lines[i])
        if match:
            # Lookahead for section header
            found_header = False
            for j in range(1, lookahead_lines+1):
                if i + j >= len(lines): break
                l2 = lines[i+j].strip().lower().rstrip(':')
                if l2 in section_names_set:
                    found_header = True
                    break
            if found_header:
                control_id = match.group(1)
                title = match.group(2).strip()
                # Find where the next control starts
                start = i+1
                end = start
                while end < len(lines):
                    next_match = control_header_regex.match(lines[end])
                    if next_match:
                        # Only next control if it also passes lookahead, otherwise keep going
                        found_next = False
                        for k in range(1, lookahead_lines+1):
                            if end + k >= len(lines): break
                            l3 = lines[end+k].strip().lower().rstrip(':')
                            if l3 in section_names_set:
                                found_next = True
                                break
                        if found_next:
                            break
                    end += 1
                block = lines[start:end]
                control = {
                    "ID": control_id, "Title": title, "Method": "",
                    "Profile Applicability": "",
                    "Description": "",
                    "Rationale": "",
                    "Impact": "",
                    "Audit": "",
                    "Audit Commands": "",
                    "Remediations": "",
                    "Remediation Commands": "",
                    "Default value": "",
                    "References": "",
                    "CIS Controls": "",
                    "MITRE ATT&CK Mappings": "",
                    "Compliant": "",
                    "Ranking Score": None,
                    "Additional Information": "",
                }

                current_field = None
                field_buffer = []
                idx2 = 0
                while idx2 < len(block):
                    line = block[idx2].strip()
                    lower_line = line.lower().rstrip(':')
                    is_header = False
                    header_candidate = None
                    if lower_line in section_names_set:
                        is_header = True
                        header_candidate = lower_line
                        if idx2 + 1 < len(block) and block[idx2+1].strip() == ":":
                            idx2 += 1
                    elif ':' in lower_line:
                        candidate = lower_line.split(':')[0].strip()
                        if candidate in section_names_set:
                            is_header = True
                            header_candidate = candidate
                    if is_header:
                        if current_field and field_buffer:
                            control[current_field] = " ".join(field_buffer).strip()
                        canon_field = header_map.get(header_candidate, header_candidate.title())
                        current_field = canon_field
                        field_buffer = []
                    else:
                        if current_field:
                            field_buffer.append(line)
                    idx2 += 1
                if current_field and field_buffer:
                    control[current_field] = " ".join(field_buffer).strip()
                controls.append(control)
            i += 1
            continue
        # Case 2: Control number on own line, title on next line
        match2 = re.match(r"^(\d+(?:\.\d+)+)\s*$", lines[i])
        if match2 and i+1 < len(lines):
            found_header = False
            for j in range(1, lookahead_lines+2):
                if i + j >= len(lines): break
                l2 = lines[i+j].strip().lower().rstrip(':')
                if l2 in section_names_set:
                    found_header = True
                    break
            if found_header:
                control_id = match2.group(1)
                title = lines[i+1].strip()
                start = i+2
                end = start
                while end < len(lines):
                    next_match = control_header_regex.match(lines[end])
                    if next_match:
                        found_next = False
                        for k in range(1, lookahead_lines+1):
                            if end + k >= len(lines): break
                            l3 = lines[end+k].strip().lower().rstrip(':')
                            if l3 in section_names_set:
                                found_next = True
                                break
                        if found_next:
                            break
                    end += 1
                block = lines[start:end]
                control = {
                    "ID": control_id, "Title": title, "Method": "",
                    "Profile Applicability": "",
                    "Description": "",
                    "Rationale": "",
                    "Impact": "",
                    "Audit": "",
                    "Audit Commands": "",
                    "Remediations": "",
                    "Remediation Commands": "",
                    "Default value": "",
                    "References": "",
                    "CIS Controls": "",
                    "MITRE ATT&CK Mappings": "",
                    "Compliant": "",
                    "Ranking Score": None,
                    "Additional Information": "",
                }
                current_field = None
                field_buffer = []
                idx2 = 0
                while idx2 < len(block):
                    line = block[idx2].strip()
                    lower_line = line.lower().rstrip(':')
                    is_header = False
                    header_candidate = None
                    if lower_line in section_names_set:
                        is_header = True
                        header_candidate = lower_line
                        if idx2 + 1 < len(block) and block[idx2+1].strip() == ":":
                            idx2 += 1
                    elif ':' in lower_line:
                        candidate = lower_line.split(':')[0].strip()
                        if candidate in section_names_set:
                            is_header = True
                            header_candidate = candidate
                    if is_header:
                        if current_field and field_buffer:
                            control[current_field] = " ".join(field_buffer).strip()
                        canon_field = header_map.get(header_candidate, header_candidate.title())
                        current_field = canon_field
                        field_buffer = []
                    else:
                        if current_field:
                            field_buffer.append(line)
                    idx2 += 1
                if current_field and field_buffer:
                    control[current_field] = " ".join(field_buffer).strip()
                controls.append(control)
            i += 2
            continue
        i += 1
    return controls