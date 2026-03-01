# SCRAM: Anti-Forensics & Dead Man's Switch Framework

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-V1.0_Active-brightgreen.svg)
![Warning](https://img.shields.io/badge/Warning-Highly_Destructive-red.svg)

**SCRAM** is a modular, kernel-integrated anti-forensics defense system designed to protect sensitive Linux environments from unauthorized physical access, forensic imaging, and hostile data extraction. 

It operates as an invisible Systemd daemon, waiting for asynchronous hardware or software triggers to execute terminal lockdown procedures or total system annihilation.

---

## ⚠️ CRITICAL WARNING ⚠️
**This software is highly destructive by design.** The `Vanish` protocol will permanently shred targeted files, obliterate the SCRAM source code, sever network connections, spoof MAC addresses, and aggressively scrub physical RAM (`sdmem`). **There is no recovery.** Do not deploy this on a primary workstation without a full understanding of the configuration. The author assumes absolutely no liability for destroyed data.

---

## 🛡️ Core Architecture (V1.0)

SCRAM is divided into three primary layers:

### 1. The Sentry Layer (Triggers)
* **Hardware Firewall (`udev`):** Instantly drops the hammer if an unauthorized, non-whitelisted USB drive is inserted into the machine.
* **Canary Software Tripwire (`pyinotify`):** A silent watcher daemon that monitors a decoy file (e.g., `Crypto_Wallets.txt`). If an intruder opens the file, SCRAM detonates.
* **Global Panic Command:** A system-wide `/usr/local/bin/vanish` command that allows instant execution of the Ghost Protocol from any directory.

### 2. The Brain (Central Command)
* **Multithreaded Daemon:** Runs entirely in the background via `systemd` (`scram.service`).
* **The Trap Room:** Aggressive signal trapping. If an intruder attempts to bypass the terminal prompt via `Ctrl+C` or `Ctrl+Z`, the system registers a hostile act and instantly detonates.
* **Duress Protocol:** Recognizes the difference between a real disarm password and a fake panic password, instantly dropping the countdown to zero if forced under duress.

### 3. The Muscle Layer (Payloads)
* **Bunker Mode:** Uses the Linux Magic SysRq key to completely bypass standard permissions, forcing the entire root filesystem into a frozen, Read-Only state.
* **Vanish Mode (Ghost Protocol):** - Severs all active network interfaces.
  - Cryptographically spoofs the hardware MAC address.
  - Shreds designated high-value target files (`shred -u -z`).
  - Initiates self-deletion of the SCRAM framework.
  - Wipes physical memory via `sdmem` to prevent cold-boot RAM attacks.

---

## ⚙️ Installation & Deployment

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/theimmortalcreator/SCRAM.git](https://github.com/theimmortalcreator/SCRAM.git)
   cd SCRAM