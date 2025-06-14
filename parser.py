#! Copilot V6

import re

def parse_text(text_path):
    """
    Robust CIS Benchmark parser:
    - Handles multi-line headings (control number + title on separate lines)
    - Extracts ID and Title for every control (best-effort)
    - Always outputs Profile Applicability as a list
    - Tolerant to section header variations (case, Statement/Procedure, etc.)
    - Defensive for missing/optional sections and avoids blank IDs/titles
    - Avoids false positives (references, appendix, etc.)
    """
    # State flags for section fields
    flagStart = False
    flagName = flagLevel = flagDesc = flagRation = flagImpact = False
    flagAudit = flagRemed = flagDefval = flagRefs = flagControl = flagMetre = False

    # Buffers for each field
    cis_name = cis_level = cis_desc = cis_ration = cis_impact = ""
    cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""

    def extract_id_and_title(control_heading):
        """Extracts control number (ID) and title, even if multi-line."""
        lines = [l.strip() for l in control_heading.strip().splitlines() if l.strip()]
        if not lines:
            return "", ""
        id_match = re.match(r"^((\d+\.)+\d+)", lines[0])
        if id_match:
            numeric_part = id_match.group(1)
            title_rest = lines[0][len(numeric_part):].lstrip(" .-")
            if title_rest:
                cleaned_title = title_rest
            elif len(lines) > 1:
                cleaned_title = lines[1]
            else:
                cleaned_title = ""
        else:
            for idx, line in enumerate(lines[1:], 1):
                id_match = re.match(r"^((\d+\.)+\d+)", line)
                if id_match:
                    numeric_part = id_match.group(1)
                    title_rest = line[len(numeric_part):].lstrip(" .-")
                    if title_rest:
                        cleaned_title = title_rest
                    elif idx + 1 < len(lines):
                        cleaned_title = lines[idx + 1]
                    else:
                        cleaned_title = ""
                    break
            else:
                numeric_part = ""
                cleaned_title = lines[0]
        cleaned_title = cleaned_title.strip()
        if not cleaned_title and len(lines) > 1:
            for l in lines[1:]:
                if l.strip():
                    cleaned_title = l.strip()
                    break
        return numeric_part, cleaned_title

    listObj = []
    with open(text_path, 'r', encoding='utf-8') as filer:
        lines = [l.rstrip('\n\r') for l in filer]
        n = len(lines)
        i = 0
        while i < n:
            line = lines[i]

            # --- Multi-line heading: number only, next line is title
            num_match = re.match(r"^((\d+\.)+\d+)\s*$", line.strip())
            if num_match and (i + 1 < n) and lines[i + 1].strip():
                cis_name = f"{num_match.group(1)} {lines[i+1].strip()}"
                i += 2
                flagStart = True
                flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                    True, False, False, False, False, False, False, False, False, False, False
                continue

            # --- Normal heading: number and title on same line
            if re.match(r"^(\d{1,2}(?:\.\d{1,2}){1,4})\s+\S+", line):
                # FLUSH previous control if any
                if cis_name.strip():
                    numeric_part, cleaned_title = extract_id_and_title(cis_name)
                    if numeric_part or cleaned_title:
                        # Section post-processing
                        def norm(x): return x.replace(' \n\n','').replace('\n\n','').rstrip()
                        cis_desc, cis_ration, cis_impact = map(norm, (cis_desc, cis_ration, cis_impact))
                        cis_audit, cis_remed, cis_defval = map(norm, (cis_audit, cis_remed, cis_defval))
                        cis_control, cis_metre = map(norm, (cis_control, cis_metre))
                        # Profile Applicability as list
                        cis_levels = [l.strip() for l in cis_level.strip().split('\n') if l.strip()] if cis_level else []
                        # References as list
                        cis_refs_list = [r.strip() for r in cis_refs.strip().split('\n') if r.strip()] if cis_refs else []
                        # Compose control object
                        x = {
                            "ID": numeric_part,
                            "Title": cleaned_title or (cis_name.strip().split(maxsplit=1)[1] if len(cis_name.strip().split(maxsplit=1))>1 else ""),
                            "Method": "",
                            "Profile Applicability": cis_levels,
                            "Description": cis_desc.strip(),
                            "Rationale": cis_ration.strip(),
                            "Impact": cis_impact.strip(),
                            "Audit": cis_audit.strip(),
                            "Audit Commands": "",
                            "Remediations": cis_remed.strip(),
                            "Remediation Commands": "",
                            "Default value": cis_defval.strip(),
                            "References": cis_refs_list,
                            "CIS Controls": [],
                            "MITRE ATT&CK Mappings": [],
                            "Compliant": "",
                            "Ranking Score": None
                        }
                        listObj.append(x)
                    # Reset fields
                    cis_name = cis_level = cis_desc = cis_ration = cis_impact = ""
                    cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""
                # Start new control
                cis_name = line.strip()
                flagStart = True
                flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                    True, False, False, False, False, False, False, False, False, False, False
                i += 1
                continue

            # --- Section headers (robust/variant matching) ---
            if flagStart:
                norm_line = line.strip().lower()
                if any(h in norm_line for h in ["page", "p a g e"]):
                    i += 1
                    continue
                # Profile Applicability (bullets/indented/multi-line)
                if "profile applicability:" in norm_line:
                    flagName, flagLevel = False, True
                elif "description:" in norm_line:
                    flagLevel, flagDesc = False, True
                elif re.search(r"rationale statement:|rationale:", norm_line):
                    flagDesc, flagRation = False, True
                elif re.search(r"impact statement:|impact:", norm_line):
                    flagRation, flagImpact = False, True
                elif re.search(r"^audit procedure:|^audit:", norm_line):
                    flagImpact, flagAudit = False, True
                elif re.search(r"^remediation procedure:|^remediation:", norm_line):
                    flagAudit, flagRemed = False, True
                elif "default value:" in norm_line:
                    flagRemed, flagDefval = False, True
                elif "references:" in norm_line:
                    flagDefval, flagRefs = False, True
                elif "cis controls:" in norm_line:
                    flagRefs, flagControl = False, True
                elif "mitre att&ck mappings:" in norm_line:
                    flagControl, flagMetre = False, True
                elif "this section is intentionally blank" in norm_line or "this section contains" in norm_line:
                    flagName = flagLevel = flagDesc = flagRation = flagImpact = flagAudit = flagRemed = flagDefval = flagRefs = flagControl = flagMetre = False
                    cis_name = cis_level = cis_desc = cis_ration = cis_impact = cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""
                    flagStart = False
                    i += 1
                    continue
                # Field content
                if flagName:
                    cis_name += ('\n' if cis_name else '') + line.strip()
                if flagLevel:
                    val = line.replace('Profile Applicability:', '').replace('•', '').strip()
                    if val: cis_level += val + "\n"
                if flagDesc:
                    cis_desc += line.replace('Description:', '').strip() + " "
                if flagRation:
                    cis_ration += line.replace('Rationale:', '').replace('Rationale Statement:', '').strip() + " "
                if flagImpact:
                    cis_impact += line.replace('Impact:', '').replace('Impact Statement:', '').strip() + " "
                if flagAudit:
                    cis_audit += line.replace('Audit:', '').replace('Audit Procedure:', '').strip() + " "
                if flagRemed:
                    cis_remed += line.replace('Remediation:', '').replace('Remediation Procedure:', '').strip() + " "
                if flagDefval:
                    cis_defval += line.replace('Default Value:', '').strip() + " "
                if flagRefs:
                    ref_line = line.replace('References:', '').strip()
                    if ref_line: cis_refs += ref_line + "\n"
                if flagControl:
                    cis_control += line.replace('CIS Controls:', '').strip() + " "
                if flagMetre:
                    cis_metre += line.replace('MITRE ATT&CK Mappings:', '').strip() + " "
            i += 1

        # Final flush for last control
        if cis_name.strip():
            numeric_part, cleaned_title = extract_id_and_title(cis_name)
            if numeric_part or cleaned_title:
                def norm(x): return x.replace(' \n\n', '').replace('\n\n', '').rstrip()
                cis_desc, cis_ration, cis_impact = map(norm, (cis_desc, cis_ration, cis_impact))
                cis_audit, cis_remed, cis_defval = map(norm, (cis_audit, cis_remed, cis_defval))
                cis_control, cis_metre = map(norm, (cis_control, cis_metre))
                cis_levels = [l.strip() for l in cis_level.strip().split('\n') if l.strip()] if cis_level else []
                cis_refs_list = [r.strip() for r in cis_refs.strip().split('\n') if r.strip()] if cis_refs else []
                x = {
                    "ID": numeric_part,
                    "Title": cleaned_title or (cis_name.strip().split(maxsplit=1)[1] if len(cis_name.strip().split(maxsplit=1))>1 else ""),
                    "Method": "",
                    "Profile Applicability": cis_levels,
                    "Description": cis_desc.strip(),
                    "Rationale": cis_ration.strip(),
                    "Impact": cis_impact.strip(),
                    "Audit": cis_audit.strip(),
                    "Audit Commands": "",
                    "Remediations": cis_remed.strip(),
                    "Remediation Commands": "",
                    "Default value": cis_defval.strip(),
                    "References": cis_refs_list,
                    "CIS Controls": [],
                    "MITRE ATT&CK Mappings": [],
                    "Compliant": "",
                    "Ranking Score": None
                }
                listObj.append(x)
    return listObj


