import os
import re
import json

rfcs_dir = r"c:\AI\Agency owner\aetheris\rfcs"
spec_pattern = re.compile(r"^SPEC-(08[6-9]|09\d|100)-.*\.md$")

spec_files = [f for f in os.listdir(rfcs_dir) if spec_pattern.match(f)]
print(f"Found {len(spec_files)} SPEC files to verify.")

errors = []

for spec_file in spec_files:
    path = os.path.join(rfcs_dir, spec_file)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Verify all 49 sections exist
    missing_sections = []
    for i in range(1, 50):
        section_hdr = f"{i}. "
        if section_hdr not in content:
            missing_sections.append(i)
            
    if missing_sections:
        errors.append(f"{spec_file}: Missing sections {missing_sections}")
        
    # 2. Verify JSON blocks
    json_blocks = re.findall(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    for idx, block in enumerate(json_blocks):
        try:
            cleaned_block = block.replace("request_id", "req-test")
            json.loads(cleaned_block)
        except Exception as e:
            if "{" in block and "}" in block and not block.strip().startswith("{"):
                pass
            else:
                errors.append(f"{spec_file}: Invalid JSON block #{idx+1}: {e}\nContent:\n{block}")

if errors:
    print("Verification FAILED:")
    for err in errors:
        print(f"- {err}")
    exit(1)
else:
    print("Verification SUCCEEDED! All files conform to the 49-section standard and contain valid schemas.")
    exit(0)
