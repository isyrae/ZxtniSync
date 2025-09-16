# ZxtniSync

**A next-gen Telegram multi-account forwarder — shielded with protection, powered by adaptive rate-limits, and driven by intelligent sync to keep your channels safe, fast, and always in perfect flow.**

---

## Features
- Secure access with remote SHA256-verified password  
- Multi-account forwarding (run multiple accounts in parallel)  
- Protection and flood-wait handling (auto wait, resume, no lost progress)  
- Progress bars with ETA per account  
- Auto profile update (name, bio, and remote profile picture)  
- Adaptive speed modes: `safe`, `standard`, `max`  
- Full logging into `zxtni_logs.txt`  
- Smart range splitting across accounts  
- Graceful shutdown with saved progress  

---

## Installation

Clone this repository and run the script:

```bash
git clone https://github.com/isyrae/ZxtniSync.git
cd ZxtniSync
python3 zxtni.py
```

The script automatically installs all requirements (`Telethon`, `tqdm`, `requests`, `Pillow`) with fallbacks to system pip or a local virtual environment.  
No manual setup is needed.

---

## Password Protection
The script checks a password hosted remotely:

- Only users with the correct password can run it  
To generate a hash for a new password:

---

## Usage
1. On first run, specify how many accounts you want to add  
2. Enter the **API ID** and **API Hash** for each account  
3. Select the source channel (applies to all accounts)  
4. Select the destination channel (applies to all accounts)  
5. Enter the message range (e.g., `20000-25000`) or `all`  
6. Choose speed mode:  
   - `safe` → maximum protection (3s delay)  
   - `standard` → balanced (1s delay)  
   - `max` → fastest possible  

The script then runs with an ASCII banner, a tagline, and live progress bars.

---

## File Structure
- `zxtni_config.json` — account configuration  
- `zxtni_progress.json` — progress tracking (resume on restart)  
- `zxtni_logs.txt` — logs of all actions  
- `.zxtni_profile.png` — temporary profile picture cache  

---

## License
This project is released under **AGPL-3.0** for maximum protection.  
Any modifications deployed publicly (including SaaS) must release their source code.  

---

## Credits
Created and maintained by [@iNToLogs](https://telegram.me/iNToLogs)  
Made with ❤️ by Rahul — [www.isyrae.xyz](https://www.isyrae.xyz)
