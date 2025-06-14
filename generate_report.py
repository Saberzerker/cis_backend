
import re

def parse_text(text_path, section_headers, lookahead_lines=3):
    from utils import log

    log(f"[+] Parsing Text Files: {text_path}")
    flagStart = False
    # All Other Flag details initialized to False
    flagName = flagLevel = flagDesc = flagRation = flagImpact = flagAudit = flagRemed = flagDefval = flagRefs = flagControl = flagMetre = False
    cis_name = cis_level = cis_desc = cis_ration = cis_impact = cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""

    listObj = []
    with open(text_path, 'r', encoding='utf-8') as filer:
        lines = filer.readlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            # Match any control like 1.1, 1.1.1, 1.1.1.1, ... (at least 1 dot)
            control_match = re.match(r"^(\d{1,2}(?:\.\d{1,2}){1,4})\s+(.+)", line)
            is_control = False
            if control_match:
                # Look ahead for section headers in next N lines to confirm it's a control, not just a heading
                for j in range(1, lookahead_lines+1):
                    if i+j < len(lines):
                        next_line = lines[i+j]
                        if any(header in next_line for header in section_headers):
                            is_control = True
                            break
            if is_control:
                if cis_name != "" and cis_desc:
                    # (Same logic as before for field extraction)
                    cis_name = cis_name.replace(' \n\n','').replace('\n\n','').rstrip()
                    cis_desc = cis_desc.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n',).rstrip()
                    cis_ration = cis_ration.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    cis_impact = cis_impact.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    cis_audit = cis_audit.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    cis_defval = cis_defval.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    cis_refs = cis_refs.rstrip()
                    cis_refs = cis_refs.strip().split('\n')
                    cis_refs = [item.strip() for item in cis_refs if item]
                    cis_level = cis_level.split('\n')
                    cis_level = [item.strip() for item in cis_level if item]
                    cis_control = cis_control.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    cis_metre = cis_metre.replace(' \n\n','XMXM').replace('\n','').replace('XMXM','\n\n').rstrip()
                    pattern = r"(#\s*.*|[A-Za-z]+\\[^\n]*)(?=\n|$)"

                    if "Appendix" in cis_control:
                        cis_control = cis_control[:cis_control.index("Appendix")]
                    if "Appendix" in cis_metre:
                        cis_metre = cis_metre[:cis_metre.index("Appendix")]

                    match = re.search(pattern, cis_audit, re.DOTALL)
                    if match:
                        main_audit_text = cis_audit[:match.start()].strip()
                        code_block_text = cis_audit[match.start():].strip()
                    else:
                        main_audit_text = cis_audit
                        code_block_text = ""

                    match = re.search(pattern, cis_remed, re.DOTALL)
                    if match:
                        main_remed_text = cis_remed[:match.start()].strip()
                        remed_code_block_text = cis_remed[match.start():].strip()
                    else:
                        main_remed_text = cis_remed
                        remed_code_block_text = ""

                    match = re.match(r"^((\d+\.)+\d+)\s+(.*)", cis_name, re.DOTALL)
                    if match:
                        numeric_part = match.group(1)
                        cleaned_title = match.group(3).strip()
                    else:
                        numeric_part = ""
                        cleaned_title = cis_name

                    title = cleaned_title
                    method = ""
                    pattern = r"\((.*?)\)"
                    match = re.search(pattern, cis_name)
                    if match:
                        method = match.group(1)
                        title = re.sub(pattern, '', cleaned_title).strip()

                    # CIS Controls parsing
                    if not cis_control.strip():
                        result = []
                    else:
                        cleaned_text = re.sub(r"(IG \d|\u25cf)", "", cis_control).strip()
                        pattern = r"(v\d+)\s+([\d.]+ [^\v]+?(?=(v\d+|$)))"
                        matches = re.findall(pattern, cleaned_text)
                        result = [{"Controls Version": match[0], "Control": match[1].strip()} for match in matches]

                    # MITRE ATT&CK Mappings
                    formatted_data = []
                    if cis_metre:
                        components = cis_metre.split()
                        keys = ["Techniques / Sub-techniques", "Tactics", "Mitigations"]
                        data = {key: [] for key in keys}
                        for component in components:
                            if component.startswith("T1"):
                                data["Techniques / Sub-techniques"].append(component)
                            elif component.startswith("TA"):
                                data["Tactics"].append(component)
                            elif component.startswith("M1") and not component.startswith("Techniques"):
                                data["Mitigations"].append(component)
                        formatted_data = [
                            {
                                "Techniques / Sub-techniques": ", ".join(data["Techniques / Sub-techniques"]),
                                "Tactics": ", ".join(data["Tactics"]),
                                "Mitigations": ", ".join(data["Mitigations"]),
                            }
                        ]

                    x = {
                        'ID': numeric_part,
                        'Title': title,
                        'Method': method,
                        'Profile Applicability': cis_level,
                        'Description': cis_desc,
                        'Rationale': cis_ration,
                        'Impact': cis_impact,
                        'Audit': main_audit_text,
                        'Audit Commands': code_block_text,
                        'Remediations': main_remed_text,
                        'Remediation Commands': remed_code_block_text,
                        'Default value': cis_defval,
                        'References': cis_refs,
                        'CIS Controls': result,
                        'MITRE ATT&CK Mappings': formatted_data,
                        'Compliant': "",
                    }
                    listObj.append(x)

                # Reset for next control
                cis_name = cis_level = cis_desc = cis_ration = cis_impact = cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""
                flagStart = True
                flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = True, False, False, False, False, False, False, False, False, False, False
                i += 1
                continue

            if flagStart:
                if any(h in line for h in ["Page", "P a g e"]):
                    i += 1
                    continue
                if "Profile Applicability:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, True, False, False, False, False, False, False, False, False, False
                if "Description:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, True, False, False, False, False, False, False, False, False
                if "Rationale:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, True, False, False, False, False, False, False, False
                if "Impact:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, True, False, False, False, False, False, False
                if re.match(r"^Audit:", line):
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, True, False, False, False, False, False
                if "Remediation:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, False, True, False, False, False, False
                if "Default Value:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, False, False, True, False, False, False
                if "References:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, False, False, False, True, False, False
                if "CIS Controls:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, False, False, False, False, True, False
                if "MITRE ATT&CK Mappings:" in line:
                    flagName, flagLevel, flagDesc, flagRation, flagImpact, flagAudit, flagRemed, flagDefval, flagRefs, flagControl, flagMetre = \
                        False, False, False, False, False, False, False, False, False, False, True
                if "This section is intentionally blank and exists to ensure" in line or "This section contains" in line:
                    flagName = flagLevel = flagDesc = flagRation = flagImpact = flagAudit = flagRemed = flagDefval = flagRefs = flagControl = flagMetre = False
                    cis_name = cis_level = cis_desc = cis_ration = cis_impact = cis_audit = cis_remed = cis_defval = cis_refs = cis_control = cis_metre = ""
                    flagStart = False
                    i += 1
                    continue
                if flagName:
                    cis_name += line
                if flagLevel:
                    cis_level += line.replace('Profile Applicability: \n', '').replace('•  ', '').replace(' \n', '\n')
                if flagDesc:
                    cis_desc += line.replace('Description: \n', '')
                if flagRation:
                    cis_ration += line.replace('Rationale: \n', '')
                if flagImpact:
                    cis_impact += line.replace('Impact: \n', '')
                if flagAudit:
                    cis_audit += line.replace('Audit: \n', '')
                if flagRemed:
                    cis_remed += line.replace('Remediation: \n', '')
                if flagDefval:
                    cis_defval += line.replace('Default Value: \n', '')
                if flagRefs:
                    if "Additional Information" in line:
                        flagRefs = False
                        i += 1
                        continue
                    line = line.replace('References: ', '').strip()
                    if re.match(r'^\d+\.\s', line):
                        cis_refs += "\n" + line
                    else:
                        cis_refs += "" + line
                if flagControl:
                    cis_control += line.replace('CIS Controls: \n', '')
                if flagMetre:
                    cis_metre += line.replace('MITRE ATT&CK Mappings: \n', '')
            i += 1
    return listObj