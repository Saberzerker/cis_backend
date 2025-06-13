from .utils import log

def validate_parsed_data(items):
    issues = []
    for idx, x in enumerate(items):
        if not x.get('ID'):
            issues.append(f"Missing ID in item {idx}")
        if not x.get('Title'):
            issues.append(f"Missing Title in item {idx}")
        if not x.get('Description'):
            issues.append(f"Missing Description in item {idx}")
        # Add more field checks as needed
    if issues:
        for issue in issues:
            log(f"[VALIDATION] {issue}", "warning")
    else:
        log("[+] Validation passed: No missing critical fields.")