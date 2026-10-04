# ========================================
# FILE CAU HINH - SUA ICON / FONT O DAY
# ========================================

# Icon cho category (theo thu tu)
CATEGORY_ICONS = ["📢", "💬", "🎮", "📚", "🎨", "🛠️", "🎉", "💼", "🌐"]

# Icon cho kenh text
TEXT_ICONS = ["💬", "📌", "🖼️", "🎵", "🎮", "📚", "🤖", "📣", "📜", "🎭"]

# Icon cho kenh voice
VOICE_ICONS = ["🔊", "🎮", "🎵", "🎙️"]

# Icon cho role
ROLE_ICONS = {
    "Admin": "👑",
    "Moderator": "🛡️",
    "VIP": "⭐",
    "Member": "👤",
    "Bot": "🤖",
    "Gamer": "🎮",
    "Hoc Vien": "🎓",
    "Tro Giang": "⭐",
    "Boosters": "💎",
}


# ===== FONT FANCY =====
def fancy(text: str) -> str:
    """Chuyen chu thanh fancy bold Unicode: abc -> abc (in dam)."""
    mapping = {}
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        mapping[c] = chr(0x1D41A + i)
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        mapping[c] = chr(0x1D400 + i)
    return "".join(mapping.get(ch, ch) for ch in text)


def small_caps(text: str) -> str:
    """Chuyen chu thanh small caps Unicode."""
    import re
    return re.sub(r"[a-z]", lambda m: chr(ord(m.group()) + 0x1D00), text)


# ===== PRESET SERVER =====
PRESETS = {
    "gaming": {
        "cats": ["Khu Vuc Gaming", "Thong Tin", "Cong Dong", "Leo Rank"],
        "channels": {
            "Khu Vuc Gaming": ["game-chung", "fps", "moba", "giai-dau"],
            "Thong Tin": ["thong-bao", "noi-quy", "su-kien"],
            "Cong Dong": ["tan-gau", "media", "bot-commands"],
            "Leo Rank": ["tim-dong-doi", "thanh-tich", "rank-voice"],
        },
        "roles": ["Admin", "Moderator", "Gamer", "VIP", "Member"],
    },
    "study": {
        "cats": ["Hoc Tap", "Thong Tin", "Thao Luan", "Luyen Tap"],
        "channels": {
            "Hoc Tap": ["tai-lieu", "toan", "khoa-hoc", "tieng-anh"],
            "Thong Tin": ["thong-bao", "noi-quy", "lich-hoc"],
            "Thao Luan": ["hoi-dap", "study-together", "bot-commands"],
            "Luyen Tap": ["bai-tap", "xep-hang", "study-voice"],
        },
        "roles": ["Admin", "Moderator", "Hoc Vien", "Tro Giang", "Member"],
    },
    "community": {
        "cats": ["Thong Tin", "Tro Chuyen", "Giai Tri", "Voice Chat"],
        "channels": {
            "Thong Tin": ["chao-mung", "thong-bao", "noi-quy", "chon-role"],
            "Tro Chuyen": ["tong-hop", "media", "meme", "bot-commands"],
            "Giai Tri": ["am-nhac", "mini-game", "phim", "nghe-thuat"],
            "Voice Chat": ["voice-chung", "gaming-voice", "music-voice"],
        },
        "roles": ["Admin", "Moderator", "VIP", "Boosters", "Member"],
    },
}


# ===== HAM THEM ICON =====
def add_icon_to_category(name: str, index: int) -> str:
    """Them icon vao truoc ten category."""
    icon = CATEGORY_ICONS[index % len(CATEGORY_ICONS)]
    return f"{icon} {name}"


def add_icon_to_channel(name: str, index: int = 0, is_voice: bool = False) -> str:
    """Them icon vao truoc ten kenh."""
    if is_voice:
        icon = VOICE_ICONS[index % len(VOICE_ICONS)]
    else:
        icon = TEXT_ICONS[index % len(TEXT_ICONS)]
    return f"{icon}-{name}"


def add_icon_to_role(name: str) -> str:
    """Them icon vao truoc ten role."""
    icon = ROLE_ICONS.get(name, "")
    return f"{icon} {name}".strip()
