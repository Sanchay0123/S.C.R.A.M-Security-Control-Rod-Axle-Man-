import os
import yaml

# 1. Calculate Paths exactly like the Brain does
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scram_config.yaml")

print(f"[*] PROBING SCRAM CONFIGURATION...")
print(f"[*] Base Directory: {BASE_DIR}")
print(f"[*] Looking for config at: {CONFIG_PATH}")

# 2. Check if file exists
if not os.path.exists(CONFIG_PATH):
    print(f"[!] CRITICAL: Config file NOT FOUND at expected path!")
else:
    print(f"[+] Config file found.")
    
    # 3. Read the file raw content (to see what is actually saved)
    print("-" * 20)
    print("RAW FILE CONTENT:")
    with open(CONFIG_PATH, 'r') as f:
        print(f.read())
    print("-" * 20)

    # 4. Parse it (to see what Python loads)
    with open(CONFIG_PATH, 'r') as f:
        data = yaml.safe_load(f)
        target = data['system'].get('self_destruct_target', 'UNKNOWN')
        
        print(f"[*] PARSED TARGET: {target}")
        
        if "/dev/sd" in target or "/dev/vd" in target:
            print(f"[!!!] DANGER: SCRIPT IS TARGETING A LIVE DRIVE!")
        else:
            print(f"[+] SAFETY CHECK PASSED: Targeting a file.")
