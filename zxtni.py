#!/usr/bin/env python3
# ===============================
# Made with ❤️ by @iNToLogs
# www.isyrae.xyz
# ===============================

import sys, subprocess, os, time, json, asyncio, signal, random, hashlib, getpass
from datetime import datetime

# ================= AUTO INSTALL REQUIREMENTS =================
def ensure_requirements():
    try:
        from telethon import TelegramClient  # noqa
        from tqdm import tqdm  # noqa
        import requests  # noqa
        from PIL import Image  # noqa
        return
    except ImportError:
        print("⚡ Installing missing requirements...")

        reqs = [
            "telethon>=1.34.0",
            "tqdm>=4.65.0",
            "requests>=2.28.0",
            "Pillow>=10.0.0"
        ]

        with open("requirements.txt", "w") as f:
            f.write("\n".join(reqs) + "\n")

        # First try with system pip (force if needed)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages"])
            return
        except subprocess.CalledProcessError:
            # Fallback → local venv
            venv_dir = ".zxtni_venv"
            if not os.path.exists(venv_dir):
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

            pip_path = os.path.join(venv_dir, "bin", "pip")
            python_path = os.path.join(venv_dir, "bin", "python")
            if os.name == "nt":  # Windows path fix
                pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
                python_path = os.path.join(venv_dir, "Scripts", "python.exe")

            subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
            os.execv(python_path, [python_path] + sys.argv)

ensure_requirements()

# ================= IMPORTS =================
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Channel, Chat
from telethon.tl import functions
from tqdm import tqdm
import requests
from PIL import Image
from io import BytesIO

# ================= PASSWORD CHECK =================
PASS_URL = "https://isyrae.xyz/zxtni_assets/pass.txt" # don't remove 

def check_password():
    try:
        r = requests.get(PASS_URL, timeout=10, headers={"User-Agent": "ZXTNI/1.0"})
        r.raise_for_status()
        online_hash = r.text.strip()
        if not online_hash or len(online_hash) != 64:
            print("❌ Password endpoint invalid.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Could not fetch password: {e}")
        sys.exit(1)

    entered = getpass.getpass("🔑 Enter password: ").strip()
    entered_hash = hashlib.sha256(entered.encode()).hexdigest()

    if entered_hash != online_hash:
        print("❌ Wrong password. Access denied.")
        sys.exit(1)
    else:
        print("✅ Access granted.")

# ================= FILES =================
CONFIG_FILE = "zxtni_config.json" # don't remove 
PROGRESS_FILE = "zxtni_progress.json" # don't remove 
LOG_FILE = "zxtni_logs.txt" # don't remove 

# ================= COLORS =================
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ================= SPEED MODES =================
SPEED_MODES = {"safe": 3, "standard": 1, "max": 0}
GLOBAL_DELAY = 1

# ================= EMOJIS & PROFILE =================
EMOJIS = ["⚡","🧿","❄️","🌀","💭","🍃","🍥","🦋","💗","🍁","🌸","🥂","🍷","👀","🥀","🍂","🗿"]
PROFILE_URL = "https://isyrae.xyz/zxtni_assets/profile.png" # don't remove 
TEMP_PROFILE = ".zxtni_profile.png" # don't remove 

# ================= LOGGING =================
def log_to_file(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def log_info(msg): print(CYAN + msg + RESET); log_to_file(msg)
def log_success(msg): print(GREEN + msg + RESET); log_to_file(msg)
def log_warn(msg): print(YELLOW + msg + RESET); log_to_file(msg)
def log_error(msg): print(RED + msg + RESET); log_to_file(msg)

# ================= ANIMATED BANNER =================
def rainbow_text(text):
    colors = [CYAN, GREEN, YELLOW, RED]
    out, i = "", 0
    for ch in text:
        out += colors[i % len(colors)] + ch + RESET
        i += 1
    return out

def animated_banner():
    ascii_art = [
        "███████╗██╗  ██╗████████╗███╗   ██╗██╗",
        "╚══███╔╝╚██╗██╔╝╚══██╔══╝████╗  ██║██║",
        "  ███╔╝  ╚███╔╝    ██║   ██╔██╗ ██║██║",
        " ███╔╝   ██╔██╗    ██║   ██║╚██╗██║██║",
        "███████╗██╔╝ ██╗   ██║   ██║ ╚████║██║",
        "╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝",
        "        ⚡ Z X T N I   S Y N C ⚡",
        "     Made with ❤️ by @iNToLogs",
        "          www.isyrae.xyz"
    ] # don't remove 
    for line in ascii_art:
        print(rainbow_text(line))
        time.sleep(0.05)
    print()

# ================= CONFIG / PROGRESS =================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

# ================= SETUP =================
def setup_accounts():
    log_info("\n[?] No config found. Let's set up your accounts.")
    num = int(input(GREEN + "[?] How many accounts? " + RESET))
    cfg = {}
    for i in range(1, num + 1):
        log_warn(f"\n--- Account {i} ---")
        api_id = int(input(GREEN + "API ID: " + RESET))
        api_hash = input(GREEN + "API Hash: " + RESET).strip()
        cfg[f"account{i}"] = {"api_id": api_id, "api_hash": api_hash}
    save_config(cfg)
    log_success("✅ Accounts saved.")
    return cfg

# ================= RANGE SPLIT =================
def split_range(start, end, num_parts):
    step = (end - start + 1) // num_parts
    ranges, current = [], start
    for i in range(num_parts):
        r_start = current
        r_end = end if i == num_parts - 1 else current + step - 1
        ranges.append((r_start, r_end))
        current = r_end + 1
    return ranges

def format_eta(seconds):
    if seconds < 60: return f"{seconds:.0f}s"
    elif seconds < 3600: return f"{seconds/60:.1f}m"
    else: return f"{seconds/3600:.1f}h"

# ================= PROFILE VALIDATION =================
def download_and_validate_profile(dest_path, url):
    r = requests.get(url, timeout=15, headers={"User-Agent": "ZXTNI/1.0"})
    r.raise_for_status()
    try:
        img = Image.open(BytesIO(r.content))
        # Force RGB mode
        img = img.convert("RGB")
        # Resize to max 512x512 (Telegram’s safe zone)
        img.thumbnail((512, 512))
        # Always save as JPEG (safe for Telegram)
        img.save(dest_path, format="JPEG")
    except Exception as e:
        raise RuntimeError(f"Profile image invalid: {e}")

# ================= PROFILE UPDATE =================
async def update_profile(client, acc_num):
    name = f"<{acc_num}> ᴢxᴛɴɪ ᴘʀᴏᴊᴇᴄᴛꜱ ~ @ɪɴᴛᴏʟᴏɢꜱ" # don't remove 
    bio = f"{random.choice(EMOJIS)} A ᴘᴀʀᴛ ᴏꜰ @isyraeProjects" # don't remove 

    # Download + fix image
    r = requests.get(PROFILE_URL, timeout=15, headers={"User-Agent": "ZXTNI/1.0"})
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert("RGB")
    img.thumbnail((512, 512))
    img.save(TEMP_PROFILE, "JPEG")

    # Update text profile
    await client(functions.account.UpdateProfileRequest(first_name=name, about=bio))

    # Upload image as profile photo (safe way)
    file = await client.upload_file(TEMP_PROFILE)
    await client(functions.photos.UploadProfilePhotoRequest(file=file))

    log_success(f"[account{acc_num}] 🎭 Profile updated.")


# ================= TELEGRAM OPS =================
async def choose_channel(client, prompt_text):
    dialogs = await client(GetDialogsRequest(offset_date=None, offset_id=0,
                                             offset_peer=InputPeerEmpty(),
                                             limit=200, hash=0))
    valid = [c for c in dialogs.chats if isinstance(c, (Channel, Chat))]
    log_info(f"\n{prompt_text}")
    for i, chat in enumerate(valid, start=1):
        title = getattr(chat, "title", None) or getattr(chat, "username", None) or str(chat.id)
        print(f"{i}. {title}")
    choice = int(input(GREEN + "[?] Enter number: " + RESET)) - 1
    return valid[choice]

async def forward_range(client, acc_name, source, dest, from_id, to_id, progress):
    acc_progress = progress.setdefault(acc_name, {})
    range_key = f"{from_id}-{to_id}"
    last_done = acc_progress.get(range_key, from_id - 1)
    if last_done >= to_id:
        log_success(f"[{acc_name}] ✅ Already finished {from_id} → {to_id}")
        return

    total = to_id - from_id + 1
    done = last_done - from_id + 1 if last_done >= from_id else 0
    start_time = time.time()

    bar = tqdm(total=total, desc=f"{acc_name}", unit="msg", ncols=80)
    local_delay = GLOBAL_DELAY

    async for message in client.iter_messages(source, min_id=last_done, max_id=to_id):
        try:
            await client.send_message(dest, message)
            done += 1; bar.update(1)
            acc_progress[range_key] = message.id; save_progress(progress)
            elapsed = time.time() - start_time
            speed = done / elapsed if elapsed > 0 else 0
            remaining = total - done
            eta = format_eta(remaining / speed) if speed > 0 else "??"
            bar.set_postfix({"ETA": eta})
            if local_delay > 0: await asyncio.sleep(local_delay)
        except errors.FloodWaitError as e:
            log_warn(f"[{acc_name}] ⏸ FloodWait {e.seconds}s.")
            await asyncio.sleep(e.seconds); local_delay += 1
        except Exception as e:
            log_error(f"[{acc_name}] ❌ Error {getattr(message,'id','?')}: {e}")
            await asyncio.sleep(2)
    bar.close()

async def run_account(cfg, acc_name, progress):
    acc = cfg[acc_name]
    client = TelegramClient(f"{acc_name}.session", acc["api_id"], acc["api_hash"])
    await client.start()
    acc_num = acc_name.replace("account", "")
    await update_profile(client, acc_num)
    source = await client.get_entity(acc["source"])
    dest = await client.get_entity(acc["dest"])
    for from_id, to_id in acc["ranges"]:
        await forward_range(client, acc_name, source, dest, from_id, to_id, progress)

# ================= MAIN =================
async def main():
    global GLOBAL_DELAY
    animated_banner()
    cfg = load_config() or setup_accounts()
    mode = input(GREEN + "[?] Speed mode (safe/standard/max): " + RESET).strip().lower()
    if mode not in SPEED_MODES: mode = "standard"
    GLOBAL_DELAY = SPEED_MODES[mode]; log_info(f"Using mode: {mode} | Delay {GLOBAL_DELAY}s")
    progress = load_progress()
    first_acc = next(iter(cfg))
    client = TelegramClient(f"{first_acc}.session", cfg[first_acc]["api_id"], cfg[first_acc]["api_hash"])
    await client.start()
    if not any("source" in cfg[a] for a in cfg):
        src = await choose_channel(client, "Select SOURCE channel:"); src_val = src.username or src.id
        for a in cfg: cfg[a]["source"] = src_val; save_config(cfg)
    if not any("dest" in cfg[a] for a in cfg):
        dst = await choose_channel(client, "Select DEST channel:"); dst_val = dst.username or dst.id
        for a in cfg: cfg[a]["dest"] = dst_val; save_config(cfg)
    if not any("ranges" in cfg[a] for a in cfg):
        rng = input(GREEN + "[?] Enter range (e.g. 20000-25000 or 'all'): " + RESET).strip()
        start, end = (1, 999_999_999) if rng.lower()=="all" else map(int, rng.split("-"))
        parts = split_range(start, end, len(cfg))
        for (a, r) in zip(cfg.keys(), parts): cfg[a]["ranges"] = [list(r)]
        save_config(cfg)
    await client.disconnect()
    await asyncio.gather(*[run_account(cfg, acc_name, progress) for acc_name in cfg])
    log_success("\n🎉 Done!")
    log_info("Made with ❤️ by @iNToLogs | www.isyrae.xyz")

# ================= GRACEFUL EXIT =================
def handle_sigint(sig, frame):
    print(RED + "\n👋 Exit requested." + RESET)
    print(GREEN + "Made with ❤️ by @iNToLogs | www.isyrae.xyz" + RESET)
    if os.path.exists(TEMP_PROFILE): os.remove(TEMP_PROFILE)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

if __name__ == "__main__":
    check_password()
    asyncio.run(main())
