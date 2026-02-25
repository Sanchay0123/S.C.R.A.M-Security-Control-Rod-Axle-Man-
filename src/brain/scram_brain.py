#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import yaml
import signal

# --- PATH CONFIGURATION ---
# Dynamically find the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scram_config.yaml")
MUSCLE_BIN = os.path.join(BASE_DIR, "src", "muscle", "scram_muscle")
UI_SCRIPT = os.path.join(BASE_DIR, "src", "brain", "scram_ui.py")

# --- LOAD CONFIG ---
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
        self.lock = threading.Lock()

    def start_countdown(self):
        """The Doom Clock: Ticks down to destruction."""
        self.active = True
        print(f"[*] SCRAM Watchdog Started. Time remaining: {self.timer}s")
        
        while self.active and self.timer > 0:
            time.sleep(1)
            with self.lock:
                self.timer -= 1
                # Debug print every 30s
                if self.timer % 30 == 0:
                    print(f"[!] T-Minus {self.timer} seconds...")

        if self.active and self.timer <= 0:
            self.execute_protocol_omega()

    def trigger_duress(self):
        """The Trap: Accelerates the timeline."""
        with self.lock:
            print("[*] DURESS DETECTED. Accelerating timeline.")
            # Cap the timer at 120s (or keep it lower if it already is)
            self.timer = min(self.timer, 120)

    def execute_protocol_omega(self):
        """THE END: Calls the C Muscle to wipe the VM Header."""
        target = config['system']['self_destruct_target']
        print(f"\n[!!!] EXECUTING SCRAM ON {target} [!!!]")
        
        # 1. Network Kill (Python Native)
        interface = config['system'].get('network_interface', 'eth0')
        print(f"[*] Killing Network ({interface})...")
        subprocess.run(["ip", "link", "set", interface, "down"], stderr=subprocess.DEVNULL)
        
        # 2. Header Wipe (C Muscle)
        # Calling the binary we compiled earlier
        if os.path.exists(MUSCLE_BIN):
            subprocess.run(["sudo", MUSCLE_BIN, "--self-destruct", target])
        else:
            print(f"[!] ERROR: Muscle binary not found at {MUSCLE_BIN}")

        # 3. Hard Reboot
        print("[*] Rebooting into oblivion...")
        os.system("echo b > /proc/sysrq-trigger")

# --- THE FAKE LOGIN ---
def fake_login_screen(manager):
    # Clear screen
    print("\033c", end="") 
    print("=== SCRAM PROTOCOL ACTIVE ===")
    print("SYSTEM LOCKED. AUTHENTICATION REQUIRED.")
    
    while manager.active:
        try:
            pwd = input("Password: ")
            
            safe_pw = config['general']['safe_password']
            duress_pw = config['general']['duress_password']

            if pwd == safe_pw:
                print("[+] Identity Confirmed. Disarming...")
                manager.active = False
                sys.exit(0)
            
            elif pwd == duress_pw:
                # The Trick
                manager.trigger_duress()
                print("[*] Authenticating...")
                time.sleep(2)
                # Launch UI in background
                subprocess.Popen(["python3", UI_SCRIPT])
                break 
            else:
                print("[!] Access Denied.")
        except EOFError:
            pass

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] SCRAM requires ROOT privileges to control the muscle.")
        sys.exit(1)

    manager = PanicManager()
    
    # Start the countdown in a background thread
    t = threading.Thread(target=manager.start_countdown, daemon=True)
    t.start()
    
    try:
        fake_login_screen(manager)
        # If we break out (Duress), keep the main thread alive for the timer
        while manager.active:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] KEYBOARD INTERRUPT IGNORED.")
