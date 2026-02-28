#!/usr/bin/env python3
import sys
import os
import yaml

BASE_DIR = "/home/sanchay-jain/SCRAM"
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scram_config.yaml")

def trigger_panic():
    with open("/tmp/.scram_panic", "w") as f:
        f.write("USB_PANIC")

try:
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)
except Exception:
    # If config fails to load, fail deadly.
    trigger_panic()
    sys.exit(1)

# Get whitelist from config, default to empty list if not found
whitelist = config.get('modes', {}).get('usb_sentry', {}).get('whitelist', [])

# udev will pass the ID as the first argument
if len(sys.argv) > 1:
    inserted_usb_id = sys.argv[1]
    
    if inserted_usb_id in whitelist:
        # It's a friendly drive. Stand down.
        sys.exit(0)

# If the ID wasn't in the whitelist, or no ID was passed, trigger the trap.
trigger_panic()
