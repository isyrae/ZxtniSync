#!/usr/bin/env python3
# ===============================
# ZXTNI SYNC - Enhanced Version
# Pattern & Bypass-timing modes
# Made with love by @iNToLogs 
# ===============================

import sys
import subprocess
import os
import time
import json
import asyncio
import signal
import random
import hashlib
import getpass
import platform
from datetime import datetime
from functools import partial

# ==================  Color Scheme ==================
class Colors:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ORANGE = "\033[38;5;208m"
    PINK = "\033[38;5;207m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    RESET = "\033[0m"
    CLEAR = "\033[2J\033[H"

# ================== System Detection ==================
def detect_system():
    system = platform.system().lower()
    is_termux = os.environ.get('PREFIX', '').endswith('com.termux')
    is_android = 'android' in platform.platform().lower() or is_termux
    
    return {
        'system': system,
        'is_termux': is_termux,
        'is_android': is_android,
        'is_linux': system == 'linux',
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin'
    }

# ==================  Auto-Installation ==================
def ensure_requirements():
    system_info = detect_system()
    
    print(f"{Colors.CYAN}Checking requirements...{Colors.RESET}")
    
    try:
        from telethon import TelegramClient
        from tqdm import tqdm
        import requests
        from PIL import Image
        print(f"{Colors.GREEN}All requirements already installed{Colors.RESET}")
        return
    except ImportError:
        pass
    
    print(f"{Colors.YELLOW}Installing missing requirements...{Colors.RESET}")
    
    requirements = [
        "telethon>=1.34.0",
        "tqdm>=4.65.0", 
        "requests>=2.28.0",
        "Pillow>=10.0.0"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements) + "\n")
    
    install_commands = []
    
    if system_info['is_termux']:
        install_commands = [
            ["pkg", "update", "-y"],
            ["pkg", "upgrade", "-y"],
            ["pkg", "install", "python", "python-pip", "libjpeg-turbo", "libpng", "zlib", "-y"],
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--no-cache-dir"]
        ]
    elif system_info['is_linux']:
        install_commands = [
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"],
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user"]
        ]
    elif system_info['is_windows']:
        install_commands = [
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        ]
    else:
        install_commands = [
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--user"],
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--user"]
        ]
    
    success = False
    for i, cmd in enumerate(install_commands):
        try:
            print(f"{Colors.CYAN}Step {i+1}/{len(install_commands)}: Running {' '.join(cmd[:3])}...{Colors.RESET}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}Step {i+1} successful{Colors.RESET}")
                if "requirements.txt" in ' '.join(cmd):
                    success = True
            else:
                print(f"{Colors.YELLOW}Step {i+1} failed (exit code {result.returncode}){Colors.RESET}")
                if result.stderr:
                    print(f"{Colors.DIM}Error: {result.stderr.strip()[:200]}...{Colors.RESET}")
                
                if "pkg" in cmd[0] and not system_info['is_termux']:
                    continue
                    
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Step {i+1} timed out{Colors.RESET}")
            continue
        except FileNotFoundError:
            print(f"{Colors.YELLOW}Command not found: {cmd[0]}{Colors.RESET}")
            continue
        except Exception as e:
            print(f"{Colors.YELLOW}Step {i+1} error: {e}{Colors.RESET}")
            continue
    
    if not success:
        print(f"{Colors.ORANGE}Trying virtual environment installation...{Colors.RESET}")
        try:
            venv_dir = ".zxtni_venv"
            if not os.path.exists(venv_dir):
                print(f"{Colors.CYAN}Creating virtual environment...{Colors.RESET}")
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir], timeout=120)
            
            if system_info['is_windows']:
                pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
                python_path = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                pip_path = os.path.join(venv_dir, "bin", "pip")
                python_path = os.path.join(venv_dir, "bin", "python")
            
            print(f"{Colors.CYAN}Installing packages in virtual environment...{Colors.RESET}")
            subprocess.check_call([pip_path, "install", "--upgrade", "pip"], timeout=120)
            subprocess.check_call([pip_path, "install", "-r", "requirements.txt"], timeout=300)
            
            print(f"{Colors.GREEN}Virtual environment setup complete{Colors.RESET}")
            print(f"{Colors.CYAN}Restarting with virtual environment...{Colors.RESET}")
            
            os.execv(python_path, [python_path] + sys.argv)
            
        except Exception as e:
            print(f"{Colors.RED}Virtual environment setup failed: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}Manual installation required:{Colors.RESET}")
            print(f"{Colors.CYAN}sudo apt update && sudo apt install python3-pip python3-dev libjpeg-dev{Colors.RESET}")
            print(f"{Colors.CYAN}pip3 install {' '.join(requirements)}{Colors.RESET}")
            sys.exit(1)
    
    try:
        from telethon import TelegramClient
        from tqdm import tqdm
        import requests
        from PIL import Image
        print(f"{Colors.GREEN}All requirements successfully installed!{Colors.RESET}")
    except ImportError as e:
        print(f"{Colors.RED}Installation verification failed: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please install manually and try again.{Colors.RESET}")
        sys.exit(1)

ensure_requirements()

from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Channel, Chat, PeerChannel, PeerChat
from telethon.tl import functions
from tqdm import tqdm
import requests
from PIL import Image
from io import BytesIO

# ================== Configuration ==================
CONFIG_FILE = "zxtni_config.json"
PROGRESS_FILE = "zxtni_progress.json" 
LOG_FILE = "zxtni_logs.txt"
PROFILE_URL = "https://isyrae.xyz/zxtni_assets/profile.png"
TEMP_PROFILE = ".zxtni_profile.jpg"

SPEED_MODES = {
    "safe": 3.0,
    "standard": 1.0,
    "max": 0.0,
    "super": 0.0
}

# ==================  Logging ==================
def safe_open_append(path):
    try:
        return open(path, "a", encoding="utf-8")
    except PermissionError:
        try:
            fallback_dir = "/tmp" if os.path.exists("/tmp") else os.path.expanduser("~")
            alt_path = os.path.join(fallback_dir, os.path.basename(path))
            return open(alt_path, "a", encoding="utf-8")
        except Exception:
            return None

def log_to_file(msg):
    f = safe_open_append(LOG_FILE)
    if not f:
        return
    with f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {msg}\n")

def log_info(msg):
    print(f"{Colors.CYAN}INFO: {msg}{Colors.RESET}")
    log_to_file(f"INFO: {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}SUCCESS: {msg}{Colors.RESET}")
    log_to_file(f"SUCCESS: {msg}")

def log_warn(msg):
    print(f"{Colors.YELLOW}WARNING: {msg}{Colors.RESET}")
    log_to_file(f"WARNING: {msg}")

def log_error(msg):
    print(f"{Colors.RED}ERROR: {msg}{Colors.RESET}")
    log_to_file(f"ERROR: {msg}")

def log_highlight(msg):
    print(f"{Colors.PINK}HIGHLIGHT: {msg}{Colors.RESET}")
    log_to_file(f"HIGHLIGHT: {msg}")

# ==================  Banner ==================
def rainbow_gradient_text(text):
    colors = [Colors.PURPLE, Colors.CYAN, Colors.GREEN, Colors.YELLOW, Colors.ORANGE, Colors.PINK]
    
    result = ""
    for i, char in enumerate(text):
        if char != ' ':
            color_idx = i % len(colors)
            result += f"{colors[color_idx]}{char}{Colors.RESET}"
        else:
            result += char
    return result

def animated_banner():
    print(Colors.CLEAR)
    
    banner_lines = [
        "███████╗██╗  ██╗████████╗███╗   ██╗██╗",
        "╚══███╔╝╚██╗██╔╝╚══██╔══╝████╗  ██║██║", 
        "  ███╔╝  ╚███╔╝    ██║   ██╔██╗ ██║██║",
        " ███╔╝   ██╔██╗    ██║   ██║╚██╗██║██║",
        "███████╗██╔╝ ██╗   ██║   ██║ ╚████║██║",
        "╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝"
    ]
    
    for line in banner_lines:
        print(rainbow_gradient_text(line))
        time.sleep(0.05)
    
    print()
    print(rainbow_gradient_text("        ZXTNI SYNC"))
    print()
    print(f"{Colors.CYAN}     Made with {Colors.RED}love{Colors.CYAN} by {Colors.YELLOW}@iNToLogs{Colors.RESET}")
    print(f"{Colors.DIM}          www.isyrae.xyz{Colors.RESET}")
    print()
    
    system_info = detect_system()
    platform_name = "Android Termux" if system_info['is_termux'] else f"{platform.system()}"
    print(f"{Colors.CYAN}Platform: {platform_name} | Python {platform.python_version()}{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 60}{Colors.RESET}")
    print()

# ================== Configuration Management ==================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error(f"Failed to load config: {e}")
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        log_success("Configuration saved")
    except Exception as e:
        log_error(f"Failed to save config: {e}")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_error(f"Failed to load progress: {e}")
            return {}
    return {}

def save_progress(progress):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error(f"Failed to save progress: {e}")

# ================== Account Setup ==================
def setup_accounts():
    print(f"{Colors.PURPLE}{Colors.BOLD}Account Setup{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")
    
    log_info("No configuration found. Let's set up your accounts.")
    
    while True:
        try:
            prompt = f"{Colors.CYAN}{Colors.BOLD}[?] How many accounts do you want to configure? {Colors.RESET}"
            num = int(input(prompt))
            if num <= 0:
                raise ValueError
            break
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.RED}Please enter a positive integer.{Colors.RESET}")
    
    cfg = {}
    
    for i in range(1, num + 1):
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Account {i} Configuration{Colors.RESET}")
        print(f"{Colors.DIM}{'-' * 30}{Colors.RESET}")
        
        while True:
            try:
                api_id_prompt = f"{Colors.GREEN}API ID: {Colors.RESET}"
                api_id = int(input(api_id_prompt))
                break
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}API ID must be a valid integer.{Colors.RESET}")
        
        api_hash_prompt = f"{Colors.GREEN}API Hash: {Colors.RESET}"
        api_hash = input(api_hash_prompt).strip()
        
        if not api_hash:
            print(f"{Colors.RED}API Hash cannot be empty.{Colors.RESET}")
            continue
            
        cfg[f"account{i}"] = {
            "api_id": api_id,
            "api_hash": api_hash
        }
        
        print(f"{Colors.GREEN}Account {i} configured successfully{Colors.RESET}")
    
    save_config(cfg)
    log_success("All accounts configured and saved!")
    return cfg

# ================== Utility Functions ==================
def split_range(start, end, num_parts):
    total = end - start + 1
    if num_parts <= 0:
        return []
    
    base = total // num_parts
    remainder = total % num_parts
    ranges = []
    current = start
    
    for i in range(num_parts):
        size = base + (1 if i < remainder else 0)
        if size <= 0:
            range_end = current - 1
        else:
            range_end = current + size - 1
        ranges.append((current, range_end))
        current = range_end + 1
    
    return ranges

def format_eta(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def normalize_chat_to_id(chat):
    if isinstance(chat, Channel):
        return int("-100" + str(chat.id))
    return int(chat.id)

# ================== Profile Management ==================
async def update_profile(client, acc_num):
    name = f"<{acc_num}> ZXTNI PROJECTS ~ @iNToLogs"
    bio = f"A part of @isyraeProjects"
    
    try:
        log_info(f"[account{acc_num}] Downloading profile image...")
        response = requests.get(PROFILE_URL, timeout=15, headers={"User-Agent": "ZXTNI/2.0"})
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.thumbnail((512, 512))
        img.save(TEMP_PROFILE, "JPEG", quality=95)
        
    except Exception as e:
        log_warn(f"[account{acc_num}] Failed to download profile image: {e}")
    
    try:
        await client(functions.account.UpdateProfileRequest(first_name=name, about=bio))
        
        if os.path.exists(TEMP_PROFILE):
            file = await client.upload_file(TEMP_PROFILE)
            await client(functions.photos.UploadProfilePhotoRequest(file=file))
            
            try:
                os.remove(TEMP_PROFILE)
            except:
                pass
                
        log_success(f"[account{acc_num}] Profile updated successfully")
        
    except Exception as e:
        log_warn(f"[account{acc_num}] Profile update failed (non-critical): {e}")

# ================== Channel Selection ==================
async def choose_channel(client, prompt_text):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}{prompt_text}{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * len(prompt_text)}{Colors.RESET}")
    
    try:
        dialogs = await client(GetDialogsRequest(
            offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0
        ))
        
        valid_chats = [c for c in dialogs.chats if isinstance(c, (Channel, Chat))]
        
        if not valid_chats:
            log_error("No channels or chats found!")
            return None
            
        for i, chat in enumerate(valid_chats, start=1):
            title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat.id)
            chat_type = "Channel" if isinstance(chat, Channel) else "Group"
            print(f"{Colors.CYAN}{i:2d}.{Colors.RESET} {chat_type} {Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
        
        print()
        while True:
            try:
                choice_prompt = f"{Colors.GREEN}[?] Enter number (1-{len(valid_chats)}): {Colors.RESET}"
                choice = int(input(choice_prompt)) - 1
                
                if choice < 0 or choice >= len(valid_chats):
                    raise ValueError
                    
                selected = valid_chats[choice]
                selected_title = getattr(selected, "title", None) or str(selected.id)
                log_success(f"Selected: {selected_title}")
                return selected
                
            except (ValueError, KeyboardInterrupt):
                print(f"{Colors.RED}Invalid selection. Please try again.{Colors.RESET}")
    
    except Exception as e:
        log_error(f"Failed to get channels: {e}")
        return None

# ================== Message Forwarding ==================
async def forward_range(client, acc_name, source_entity, dest_entity, from_id, to_id, 
                       progress, delay, jitter=False, pattern=None, random_mode=False):
    
    acc_progress = progress.setdefault(acc_name, {})
    range_key = f"{from_id}-{to_id}"
    last_done = acc_progress.get(range_key, from_id - 1)
    
    if last_done >= to_id:
        log_success(f"[{acc_name}] Range {from_id}-{to_id} already completed")
        return

    total = to_id - from_id + 1
    done = max(0, last_done - from_id + 1) if last_done >= from_id else 0
    start_time = time.time()

    bar = tqdm(
        total=total, desc=f"{Colors.CYAN}{acc_name}{Colors.RESET}", unit="msg", ncols=100,
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
    )
    bar.update(done)

    local_delay = delay

    try:
        async for message in client.iter_messages(source_entity, min_id=last_done, max_id=to_id):
            try:
                await client.send_message(dest_entity, message)
                done += 1
                bar.update(1)
                
                acc_progress[range_key] = message.id
                save_progress(progress)
                
                elapsed = time.time() - start_time
                speed = done / elapsed if elapsed > 0 else 0
                remaining = total - done
                eta = format_eta(remaining / speed) if speed > 0 else "INF"
                
                bar.set_postfix_str(f"ETA: {eta}")
                
                if random_mode and pattern:
                    low, high = pattern if len(pattern) >= 2 else (1.0, 3.0)
                    sleeptime = random.uniform(low, high)
                elif pattern:
                    idx = (done - 1) % len(pattern)
                    sleeptime = pattern[idx]
                    if jitter:
                        sleeptime += random.uniform(0, min(0.25, sleeptime))
                else:
                    sleeptime = local_delay
                    if jitter and local_delay > 0:
                        sleeptime += random.uniform(0, min(0.5, local_delay))
                
                if sleeptime > 0:
                    await asyncio.sleep(sleeptime)
                    
            except errors.FloodWaitError as e:
                log_warn(f"[{acc_name}] FloodWait: {e.seconds}s")
                bar.set_description_str(f"{acc_name} (FloodWait {e.seconds}s)")
                await asyncio.sleep(e.seconds)
                local_delay = max(local_delay + 1, 1.0)
                bar.set_description_str(acc_name)
                
            except Exception as e:
                log_error(f"[{acc_name}] Message {getattr(message, 'id', '?')}: {e}")
                await asyncio.sleep(2)
                
    finally:
        bar.close()

# ================== Account Runner ==================
async def run_account(cfg, acc_name, progress, global_mode, pattern_conf):
    
    acc = cfg[acc_name]
    client = TelegramClient(f"{acc_name}.session", acc["api_id"], acc["api_hash"])
    
    try:
        await client.start()
        acc_num = acc_name.replace("account", "")
        
        try:
            await update_profile(client, acc_num)
        except Exception as e:
            log_warn(f"[{acc_name}] Profile update failed: {e}")

        async def safe_get_entity(val, name):
            try:
                str_val = str(val)
                if str_val.startswith("-100"):
                    return await client.get_entity(PeerChannel(int(str_val.replace("-100", ""))))
                else:
                    return await client.get_entity(PeerChat(int(str_val)))
            except Exception as e:
                log_error(f"[{acc_name}] Cannot resolve {name} ({val}): {e}")
                raise

        source_entity = await safe_get_entity(cfg["source"], "source")
        dest_entity = await safe_get_entity(cfg["dest"], "destination")

        random_mode = False
        pattern = None
        
        if global_mode == "safe":
            delay, jitter = 3.0, True
        elif global_mode == "standard":
            delay, jitter = 1.0, True
        elif global_mode == "max":
            delay, jitter = 0.0, False
        elif global_mode == "super":
            delay, jitter = 0.0, False
        elif global_mode == "pattern":
            delay, jitter = 0.0, False
            pattern = pattern_conf.get("pattern_list", [0.5, 1.0, 2.0])
            if pattern_conf.get("mode", "rotate") == "random":
                random.shuffle(pattern)
        elif global_mode == "bypass_random":
            random_mode = True
            pattern = (pattern_conf.get("low", 1.0), pattern_conf.get("high", 3.0))
            delay, jitter = 0.0, False
        else:
            delay, jitter = 1.0, True

        for from_id, to_id in acc["ranges"]:
            await forward_range(
                client, acc_name, source_entity, dest_entity,
                from_id, to_id, progress, delay, jitter, pattern, random_mode
            )
            
    except Exception as e:
        log_error(f"[{acc_name}] Fatal error: {e}")
    finally:
        try:
            await client.disconnect()
        except:
            pass

# ================== Main Application ==================
async def main():
    animated_banner()
    
    cfg = load_config()
    if not cfg:
        cfg = setup_accounts()
    
    print(f"{Colors.PURPLE}{Colors.BOLD}Mode Selection{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")
    
    mode_descriptions = {
        "bypass": f"{Colors.RED}Randomized timing (HIGH RISK){Colors.RESET}",
        "safe": f"{Colors.GREEN}Conservative (3s delays){Colors.RESET}",
        "standard": f"{Colors.YELLOW}Balanced (1s delays){Colors.RESET}", 
        "max": f"{Colors.ORANGE}Fast (no delays){Colors.RESET}",
        "super": f"{Colors.RED}Extreme (VERY HIGH RISK){Colors.RESET}",
        "pattern": f"{Colors.PURPLE}Custom pattern{Colors.RESET}"
    }
    
    for mode, desc in mode_descriptions.items():
        print(f"  - {Colors.CYAN}{mode:<10}{Colors.RESET} - {desc}")
    
    print()
    chosen = input(f"{Colors.CYAN}{Colors.BOLD}[?] Select mode: {Colors.RESET}").strip().lower()
    
    if chosen == "bypass":
        print(f"\n{Colors.RED}WARNING: Bypass Mode{Colors.RESET}")
        print(f"{Colors.YELLOW}This will use randomized delays but won't implement true evasion.{Colors.RESET}")
        print(f"{Colors.RED}Account risk is significantly increased!{Colors.RESET}")
        
        confirm = input(f"\n{Colors.RED}{Colors.BOLD}Type 'CONFIRM' to proceed: {Colors.RESET}").strip()
        if confirm != "CONFIRM":
            log_info("Bypass mode cancelled, using safe mode")
            global_mode = "safe"
            pattern_conf = {}
        else:
            bounds_input = input(f"{Colors.CYAN}Delay range (e.g., '1 3') or Enter for default: {Colors.RESET}").strip()
            if bounds_input:
                try:
                    low, high = map(float, bounds_input.split())
                    low = max(0.1, low)
                    high = max(low + 0.5, high)
                except:
                    low, high = 1.0, 3.0
            else:
                low, high = 1.0, 3.0
            
            global_mode = "bypass_random"
            pattern_conf = {"low": low, "high": high}
            log_warn(f"Randomized timing: {low:.2f}s - {high:.2f}s per message")
    
    elif chosen == "super":
        print(f"\n{Colors.RED}EXTREME WARNING: Super Mode{Colors.RESET}")
        print(f"{Colors.RED}This mode has VERY HIGH RISK of account limitations or bans!{Colors.RESET}")
        print(f"{Colors.YELLOW}Only use if you understand the consequences.{Colors.RESET}")
        
        confirm = input(f"\n{Colors.RED}{Colors.BOLD}Type 'CONFIRM' to proceed: {Colors.RESET}").strip()
        if confirm != "CONFIRM":
            log_info("Super mode cancelled, using standard mode")
            global_mode = "standard"
            pattern_conf = {}
        else:
            global_mode = "super"
            pattern_conf = {}
            log_warn("Super mode activated - proceed with extreme caution!")
    
    elif chosen == "pattern":
        print(f"\n{Colors.PURPLE}Pattern Mode Configuration{Colors.RESET}")
        print(f"{Colors.DIM}{'-' * 35}{Colors.RESET}")
        
        pattern_input = input(f"{Colors.CYAN}Enter delays (e.g., '0.5,1,2') or Enter for default: {Colors.RESET}").strip()
        if pattern_input:
            try:
                pattern_list = [float(x.strip()) for x in pattern_input.split(",") if x.strip()]
                if not pattern_list:
                    raise ValueError
            except:
                pattern_list = [0.5, 1.0, 2.0]
                log_warn("Invalid pattern, using default: [0.5, 1.0, 2.0]")
        else:
            pattern_list = [0.5, 1.0, 2.0]
        
        mode_input = input(f"{Colors.CYAN}Sequence mode (rotate/random) [rotate]: {Colors.RESET}").strip().lower()
        mode = "random" if mode_input == "random" else "rotate"
        
        global_mode = "pattern"
        pattern_conf = {"pattern_list": pattern_list, "mode": mode}
        log_success(f"Pattern: {pattern_list} ({mode} mode)")
    
    else:
        global_mode = chosen if chosen in SPEED_MODES else "standard"
        pattern_conf = {}
        if global_mode != chosen:
            log_warn(f"Unknown mode '{chosen}', using standard mode")

    log_info(f"Selected mode: {global_mode}")
    
    # Load progress
    progress = load_progress()
    
    # Channel selection
    print(f"\n{Colors.PURPLE}{Colors.BOLD}Channel Configuration{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")
    
    first_acc = next(iter(cfg))
    client = TelegramClient(f"{first_acc}.session", cfg[first_acc]["api_id"], cfg[first_acc]["api_hash"])
    
    try:
        await client.start()
        
        if "source" not in cfg:
            src = await choose_channel(client, "Select SOURCE channel:")
            if not src:
                log_error("Source channel selection failed")
                return
            cfg["source"] = normalize_chat_to_id(src)
        
        if "dest" not in cfg:
            dst = await choose_channel(client, "Select DESTINATION channel:")
            if not dst:
                log_error("Destination channel selection failed") 
                return
            cfg["dest"] = normalize_chat_to_id(dst)
        
    finally:
        await client.disconnect()
    
    # Configure accounts
    accounts = [a for a in cfg if a.startswith("account")]
    for acc in accounts:
        cfg[acc]["source"] = cfg["source"]
        cfg[acc]["dest"] = cfg["dest"]
    
    # Range configuration
    if "ranges" not in cfg:
        print(f"\n{Colors.PURPLE}{Colors.BOLD}Range Configuration{Colors.RESET}")
        print(f"{Colors.DIM}{'-' * 30}{Colors.RESET}")
        
        range_input = input(f"{Colors.CYAN}Enter range (e.g., '20000-25000' or 'all'): {Colors.RESET}").strip()
        
        if range_input.lower() == "all":
            start, end = 1, 999_999_999
            log_info("Using full range: 1 to 999,999,999")
        else:
            try:
                parts = range_input.split("-")
                if len(parts) != 2:
                    raise ValueError
                start, end = int(parts[0].strip()), int(parts[1].strip())
                if start > end:
                    start, end = end, start
            except:
                log_warn("Invalid range format, using default: 1-10000")
                start, end = 1, 10000
        
        # Split range among accounts
        ranges = split_range(start, end, len(accounts))
        cfg["ranges"] = [list(r) for r in ranges]
        
        for i, acc in enumerate(accounts):
            cfg[acc]["ranges"] = [cfg["ranges"][i]]
    
    # Display configuration preview
    print(f"\n{Colors.PURPLE}{Colors.BOLD}Configuration Preview{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")
    
    print(f"{Colors.CYAN}Mode:{Colors.RESET} {global_mode}")
    print(f"{Colors.CYAN}Accounts:{Colors.RESET} {len(accounts)}")
    
    for i, acc in enumerate(accounts, start=1):
        r = cfg[acc]["ranges"][0]
        range_size = r[1] - r[0] + 1
        print(f"{Colors.GREEN}  Account {i}:{Colors.RESET} {r[0]:,} -> {r[1]:,} ({range_size:,} messages)")
    
    print()
    proceed = input(f"{Colors.GREEN}{Colors.BOLD}Type 'YES' to start forwarding: {Colors.RESET}").strip()
    if proceed.upper() != "YES":
        log_error("Operation cancelled by user")
        return
    
    # Save configuration
    save_config(cfg)
    
    # Start forwarding
    print(f"\n{Colors.GREEN}{Colors.BOLD}Starting ZXTNI Sync{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 30}{Colors.RESET}")
    
    start_time = time.time()
    
    try:
        await asyncio.gather(*[
            run_account(cfg, acc_name, progress, global_mode, pattern_conf) 
            for acc_name in accounts
        ])
    except KeyboardInterrupt:
        log_warn("Operation interrupted by user")
    except Exception as e:
        log_error(f"Unexpected error: {e}")
    
    # Final statistics
    elapsed_time = time.time() - start_time
    print(f"\n{Colors.GREEN}{Colors.BOLD}ZXTNI Sync Complete!{Colors.RESET}")
    print(f"{Colors.CYAN}Total time: {format_eta(elapsed_time)}{Colors.RESET}")
    print()
    log_highlight("Made with love by @iNToLogs | www.isyrae.xyz")

# ================== Signal Handling ==================
def handle_sigint(sig, frame):
    print(f"\n{Colors.YELLOW}Shutdown requested...{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}Made with love by @iNToLogs | www.isyrae.xyz{Colors.RESET}")
    
    # Cleanup
    try:
        if os.path.exists(TEMP_PROFILE):
            os.remove(TEMP_PROFILE)
    except:
        pass
    
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# ================== Entry Point ==================
if __name__ == "__main__":
    #  authentication
    PASS_URL = "https://isyrae.xyz/zxtni_assets/pass.txt"
    
    print(f"{Colors.CYAN}{Colors.BOLD}Authentication Required{Colors.RESET}")
    print(f"{Colors.DIM}{'-' * 30}{Colors.RESET}")
    
    try:
        log_info("Fetching authentication token...")
        response = requests.get(PASS_URL, timeout=10, headers={"User-Agent": "ZXTNI/2.0"})
        response.raise_for_status()
        
        online_hash = response.text.strip()
        if not online_hash or len(online_hash) != 64:
            log_error("Invalid authentication endpoint")
            sys.exit(1)
            
    except Exception as e:
        log_error(f"Authentication fetch failed: {e}")
        sys.exit(1)
    
    # Password verification
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            entered = getpass.getpass(f"{Colors.GREEN}Enter password: {Colors.RESET}").strip()
            entered_hash = hashlib.sha256(entered.encode()).hexdigest()
            
            if entered_hash == online_hash:
                log_success("Authentication successful!")
                break
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    log_error(f"Invalid password. {remaining} attempts remaining.")
                else:
                    log_error("Maximum attempts exceeded. Access denied.")
                    sys.exit(1)
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.RED}Authentication cancelled{Colors.RESET}")
            sys.exit(1)
    
    # Run main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        handle_sigint(None, None)
    except Exception as e:
        log_error(f"Fatal error: {e}")
        sys.exit(1)
