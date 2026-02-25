#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import yaml
import glob

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scram_config.yaml")
MUSCLE_BIN = os.path.join(BASE_DIR, "src", "muscle", "scram_muscle")
UI_SCRIPT = os.path.join(BASE_DIR, "src", "brain", "scram_ui.py")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"[!] Critical Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)

config = load_config()

class PanicManager:
    def __init__(self):
        self.timer = config['general'].get('watchdog_timeout', 300)
        self.active = False
        self.mode = config['general'].get('default_mode', 'bunker')
        self.lock = threading.Lock()

    def start_countdown(self):
        self.active = True
        print(f"[*] SCRAM Watchdog Started. Mode: {self.mode.upper()}. Time: {self.timer}s")
        
        while self.active and self.timer > 0:
            time.sleep(1)
            with self.lock:
                self.timer -= 1
                if self.timer % 30 == 0:
                    print(f"[!] T-Minus {self.timer} seconds...")

        if self.active and self.timer <= 0:
            self.execute_dispatch()

    def trigger_duress(self):
        with self.lock:
            print("[*] DURESS DETECTED. Accelerating timeline.")
            self.timer = min(self.timer, 120)

    def trigger_immediate_panic(self, forced_mode=None):
        """Used by the Canary or USB Sentry to bypass the timer."""
        with self.lock:
            if forced_mode:
                self.mode = forced_mode
            print(f"[!!!] IMMEDIATE PANIC TRIGGERED. MODE: {self.mode.upper()}")
            self.timer = 0 # Forces the loop to end and dispatch to run

    # --- THE DISPATCHER ---
    def execute_dispatch(self):
        print(f"\n[!!!] EXECUTING SCRAM: {self.mode.upper()} PROTOCOL [!!!]")
        
        # Always kill the network first, regardless of mode
        interface = config['system'].get('network_interface', 'eth0')
        subprocess.run(["ip", "link", "set", interface, "down"], stderr=subprocess.DEVNULL)
        
        if self.mode == "bunker":
            self._execute_bunker()
        elif self.mode == "vanish":
            self._execute_vanish()
        elif self.mode == "lockdown":
            self._execute_lockdown()
        else:
            print(f"[!] Unknown mode: {self.mode}. Defaulting to LOCKDOWN.")
            self._execute_lockdown()

    # --- THE PAYLOADS ---
    def _execute_bunker(self):
        """
        BUNKER MODE: Malware Containment.
        Cuts network, kills non-root processes, remounts /home as Read-Only.
        """
        print(f"\n[!!!] EXECUTING BUNKER MODE (MALWARE CONTAINMENT) [!!!]")
        
        # 1. Quarantine Storage (/home RO)
        print("[*] Quarantining /home directory...")
        if os.path.exists(MUSCLE_BIN):
            subprocess.run(["sudo", MUSCLE_BIN, "--quarantine"])
        else:
            print(f"[!] ERROR: Muscle binary not found at {MUSCLE_BIN}")

        # 2. The Purge (Process Killing)
        print("[*] Purging user-space processes...")
        # Get the actual user logged into the GUI, not root
        target_user = os.environ.get('SUDO_USER', os.getlogin())
        #subprocess.run(["killall", "-u", target_user], stderr=subprocess.DEVNULL)

        print("[+] BUNKER LOCKDOWN COMPLETE. System is frozen and safe.")
        
        # Optional: Lock the screen instead of rebooting, so you can investigate.
        # os.system("loginctl lock-session")

    def _execute_vanish(self):
        """The Ghost Option: Scrub traces and shutdown gracefully."""
        print("[*] VANISH: Scrubbing sensitive files...")
        try:
            paths = config['modes']['vanish'].get('target_paths', [])
        except KeyError:
            paths = []
        
        for path_pattern in paths:
            # Expand wildcards (like /tmp/*)
            for file_path in glob.glob(path_pattern):
                if os.path.isfile(file_path):
                    try:
                        # Use standard 'shred' utility to overwrite 3 times
                        subprocess.run(["shred", "-u", "-z", file_path], stderr=subprocess.DEVNULL)
                        print(f"  [+] Shredded: {file_path}")
                    except Exception as e:
                        pass
        
        print("[*] VANISH: Clearing RAM cache...")
        os.system("sync; echo 3 > /proc/sys/vm/drop_caches") 
        
        print("[+] VANISH COMPLETE. Traces scrubbed. System remains active.")
        # If you want it to kick you to the login screen instead of just sitting there, 
        # you can uncomment the next line:
        # os.system(f"loginctl terminate-user {os.environ.get('SUDO_USER', os.getlogin())} 2>/dev/null")

    def _execute_lockdown(self):
        """The Shield Option: Freeze the system, keep it running for alerts."""
        print("[*] LOCKDOWN: Freezing user sessions...")
        # Get the actual user logged into the GUI, not root
        target_user = os.environ.get('SUDO_USER', os.getlogin())
        os.system(f"loginctl terminate-user {target_user} 2>/dev/null")
        os.system(f"killall -u {target_user} 2>/dev/null")

# --- THE FAKE LOGIN ---
def fake_login_screen(manager):
    print("\033c", end="") 
    print("=== SCRAM PROTOCOL ACTIVE ===")
    
    while manager.active:
        try:
            pwd = input("Password: ")
            
            if pwd == config['general']['safe_password']:
                print("[+] Identity Confirmed. Disarming...")
                manager.active = False
                sys.exit(0)
            elif pwd == config['general']['duress_password']:
                manager.trigger_duress()
                print("[*] Authenticating...")
                time.sleep(2)
                subprocess.Popen(["python3", UI_SCRIPT])
                break 
            else:
                print("[!] Access Denied.")
        except EOFError:
            pass

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] SCRAM requires ROOT privileges.")
        sys.exit(1)

    manager = PanicManager()
    t = threading.Thread(target=manager.start_countdown, daemon=True)
    t.start()
    
    try:
        fake_login_screen(manager)
        while manager.active:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] KEYBOARD INTERRUPT IGNORED.")