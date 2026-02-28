#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import yaml
import glob
import signal
import argparse

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
        # Arm the signal traps (Ctrl+C, kill, and Ctrl+Z)
        signal.signal(signal.SIGINT, self._hostile_interrupt_handler)
        #signal.signal(signal.SIGTERM, self._hostile_interrupt_handler)
        signal.signal(signal.SIGTSTP, self._hostile_interrupt_handler)
    
    def _hostile_interrupt_handler(self, signum, frame):
        """Catches Ctrl+C or kill commands and instantly detonates SCRAM."""
        print("\n\n[!!!] HOSTILE TERMINATION ATTEMPT DETECTED [!!!]")
        print(f"[*] Signal {signum} intercepted. You cannot stop this.")
        print("[*] PENALTY: Timer dropped to ZERO.")
        
        with self.lock:
            self.timer = 0

    def start_countdown(self):
        self.active = True
        print(f"[*] SCRAM Watchdog Started. Mode: {self.mode.upper()}. Time: {self.timer}s")
        
        while self.active and self.timer > 0:
            time.sleep(1)
            with self.lock:
                # --- NEW: Check for Canary Trigger ---
                if os.path.exists("/tmp/.scram_panic"):
                    print("\n[!!!] CANARY TRIGGER DETECTED FROM SENTRY [!!!]")
                    self.timer = 0
                    os.remove("/tmp/.scram_panic") # Clean up
                    break
                # -----------------------------------
                
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
        target_user = os.environ.get('SUDO_USER', "sanchay-jain")
        #subprocess.run(["killall", "-u", target_user], stderr=subprocess.DEVNULL)

        print("[+] BUNKER LOCKDOWN COMPLETE. System is frozen and safe.")
        
        # Optional: Lock the screen instead of rebooting, so you can investigate.
        # os.system("loginctl lock-session")

    def _execute_vanish(self):
        """The Ghost Option: Spoof MAC, Scrub traces, Wipe RAM."""
        print(f"\n[!!!] EXECUTING VANISH MODE (GHOST PROTOCOL) [!!!]")
        
        # 1. Network Ghosting (MAC Spoofing)
        interface = config['system'].get('network_interface', 'eth0')
        print(f"[*] Spoofing MAC address on {interface}...")
        # Network was already taken down by the Dispatcher, so we can spoof immediately
        subprocess.run(["macchanger", "-r", interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 2. File Shredding
        print("[*] VANISH: Shredding sensitive files...")
        try:
            paths = config['modes']['vanish'].get('target_paths', [])
        except KeyError:
            paths = []
        
        for path_pattern in paths:
            # Expand wildcards (like /tmp/*)
            for file_path in glob.glob(path_pattern):
                if os.path.isfile(file_path):
                    try:
                        # Use standard 'shred' utility to overwrite 3 times securely
                        subprocess.run(["shred", "-u", "-z", file_path], stderr=subprocess.DEVNULL)
                        print(f"  [+] Shredded: {file_path}")
                    except Exception as e:
                        pass
        
        # --- NEW: SCRAM Self-Deletion ---
        print("[*] VANISH: Initiating SCRAM Self-Destruct...")
        scram_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Gets ~/SCRAM
        
        # 1. Shred all files inside the SCRAM directory recursively
        for root, dirs, files in os.walk(scram_dir, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                subprocess.run(["shred", "-u", "-z", file_path], stderr=subprocess.DEVNULL)
            
            # 2. Remove the now-empty directories
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass
        
        # 3. Remove the root SCRAM folder itself
        try:
            os.rmdir(scram_dir)
            print("  [+] SCRAM framework securely annihilated.")
        except OSError:
            pass
        # --------------------------------
        
        # 3. The RAM Wipe (Anti-Cold Boot)
        print("[*] VANISH: Wiping system RAM (This may take a moment)...")
        # sdmem -f (fast) -ll (writes zeros instead of random data for speed)
        subprocess.run(["sdmem", "-f", "-ll"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("[+] VANISH COMPLETE. Identity ghosted, data shredded, RAM cleared.")
        print("[*] System remains powered on but inert.")
        
        # Optional: Kick user to login screen
        # target_user = os.environ.get('SUDO_USER', "sanchay-jain")
        # os.system(f"loginctl terminate-user {target_user} 2>/dev/null")

    def _execute_lockdown(self):
        """The Shield Option: Freeze the system, keep it running for alerts."""
        print("[*] LOCKDOWN: Freezing user sessions...")
        # Get the actual user logged into the GUI, not root
        target_user = os.environ.get('SUDO_USER', "sanchay-jain")
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
    # --- SCRAM Command Line Interface ---
    parser = argparse.ArgumentParser(description="SCRAM Core Brain - Multi-Mode Defense System")
    parser.add_argument("--standby", action="store_true", help="Run silently, waiting for Sentry (Canary/USB) triggers to launch Bunker")
    parser.add_argument("--timer", type=int, help="Explicitly arm the Dead Man's Switch with X seconds (defaults to Bunker)")
    parser.add_argument("--vanish", action="store_true", help="Explicitly and instantly execute the Ghost Protocol")
    parser.add_argument("--bunker", action="store_true", help="Explicitly and instantly execute the Bunker Lockdown")
    
    args = parser.parse_args()

    # --- 1. Explicit Immediate Execution ---
    if args.vanish:
        print("[!] EXPLICIT OVERRIDE: VANISH MODE INITIATED")
        brain = PanicManager()
        brain.mode = "vanish"
        brain.execute_dispatch()
        sys.exit(0)

    if args.bunker:
        print("[!] EXPLICIT OVERRIDE: BUNKER MODE INITIATED")
        brain = PanicManager()
        brain.mode = "bunker"
        brain.execute_dispatch()
        sys.exit(0)

    # --- 2. Dead Man's Switch (Explicit Timer) ---
    if args.timer:
        print(f"[*] Arming Dead Man's Switch for {args.timer} seconds...")
        brain = PanicManager()
        brain.timer = args.timer
        brain.mode = "bunker" 
        brain.start_countdown()
        sys.exit(0)

    # --- 3. Standby Mode (Listening for Sentries) ---
    if args.standby:
        print("[*] SCRAM Brain is in STANDBY. Waiting for Sentry triggers...")
        brain = PanicManager()
        brain.mode = "bunker" 
        
        # Infinite silent loop looking for the trigger file
        try:
            while True:
                time.sleep(1)
                if os.path.exists("/tmp/.scram_panic"):
                    print("\n[!!!] SENTRY TRIGGER DETECTED [!!!]")
                    os.remove("/tmp/.scram_panic")
                    brain.execute_dispatch()
                    break
        except KeyboardInterrupt:
            print("\n[*] Standby mode disarmed.")
        sys.exit(0)

    # --- 4. No Arguments Provided ---
    parser.print_help()