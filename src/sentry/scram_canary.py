#!/usr/bin/env python3
import os
import sys
import pyinotify
import yaml

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scram_config.yaml")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"[!] Critical Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)

config = load_config()

class CanaryHandler(pyinotify.ProcessEvent):
    def process_IN_ACCESS(self, event):
        self.trigger_panic(event.pathname)

    def process_IN_OPEN(self, event):
        self.trigger_panic(event.pathname)

    def trigger_panic(self, filepath):
        print(f"\n[!!!] TRIPWIRE ACTIVATED: {filepath} was accessed! [!!!]")
        print("[*] Signaling SCRAM Brain...")
        
        # Create the trigger file that the Brain is watching for
        with open("/tmp/.scram_panic", "w") as f:
            f.write("PANIC")
            
        # Exit the Sentry, its job is done
        sys.exit(0)

if __name__ == "__main__":
    if not config['modes']['canary'].get('enabled', False):
        print("[-] Canary mode is disabled in config.")
        sys.exit(0)
 
    # Get the file to watch
    target_file = config['modes']['canary'].get('filepath')
    
    if not target_file:
        print("[!] No canary filepath defined in config.")
        sys.exit(1)

    # Ensure the decoy file actually exists, otherwise create it
    if not os.path.exists(target_file):
        print(f"[*] Planting decoy file at {target_file}...")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w") as f:
            f.write("Bitcoin Wallet Recovery Seed:\n1. abandon\n2. ability\n3. able\n... (DO NOT SHARE)")

    print(f"[*] SENTRY ONLINE: Watching Canary file -> {target_file}")
    
    # Set up the inotify kernel hook
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_ACCESS | pyinotify.IN_OPEN
    handler = CanaryHandler()
    notifier = pyinotify.Notifier(wm, handler)

    wm.add_watch(target_file, mask)

    try:
        # Loop forever, completely silently, waiting for the file to be touched
        notifier.loop()
    except KeyboardInterrupt:
        print("\n[*] Sentry disarming.")
