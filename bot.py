import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
PORT = int(os.getenv("PORT", 3000))

# ===== HTTP SERVER (giữ Render Free không bị sleep) =====
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Bot is alive!".encode("utf-8"))

    def log_message(self, format, *args):
        pass

def run_http_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"[HTTP] Server chay tai port {PORT}")
    server.serve_forever()

# ===== FONT FANCY =====
def fancy(text: str) -> str:
    mapping = {}
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        mapping[c] = chr(0x1D41A + i)
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        mapping[c] = chr(0x1D400 + i)
    return "".join(mapping.get(ch, ch) for ch in text)

def small_caps(text: str) -> str:
    return re.sub(r"[a-z]", lambda m: chr(ord(m.group()) + 0x1D00), text)

# ===== ICON =====
ICONS = {
    "category": ["📢", "💬", "🎮", "📚", "🎨", "🛠️", "🎉", "💼", "🌐"],
    "announce": ["📣", "🔔", "📢"],
}

# ===== MODAL NHẬP LIỆU =====
class SetupModal(discord.ui.Modal, title="Thiet lap server bang AI"):
    category_count = discord.ui.TextInput(
        label="So luong category muon tao",
        placeholder="Nhap so luong danh muc muon tao, toi da 9",
        required=True,
        max_length=1,
    )
    category_names = discord.ui.TextInput(
        label="Ten category (khong bat buoc)",
        placeholder="Vi du: Chao mung, Chung, Giai tri...",
        required=False,
        max_length=200,
    )
    description = discord.ui.TextInput(
        label="Nhap yeu cau cua ban",
        placeholder="Mo ta server ban muon (chu de, co kenh gi, quy mo cong dong...)",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            count = int(self.category_count.value)
        except ValueError:
            count = 3
        count = max(1, min(count, 9))

        user_names = [
            n.strip() for n in self.category_names.value.split(",") if n.strip()
        ] if self.category_names.value else []

        try:
            stats = await build_server(
                interaction.guild, count, user_names, self.description.value
            )

            embed = discord.Embed(
                title=f"{fancy('Setup Server Complete')}",
                description=(
                    f"{ICONS['announce'][0]} **Da thiet lap server thanh cong!**\n\n"
                    f"> 📁 **Category:** `{stats['categories']}`\n"
                    f"> 💬 **Text Channels:** `{stats['text_channels']}`\n"
                    f"> 🔊 **Voice Channels:** `{stats['voice_channels']}`\n"
                    f"> 🎭 **Roles:** `{stats['roles']}`\n\n"
                    f"*{small_caps('Chuc ban quan ly server vui ve!')}*"
                ),
                color=0x5865F2,
            )
            embed.set_footer(
                text="Powered by DobbySetup",
                icon_url=interaction.client.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"[MODAL ERROR] {e}")
            await interaction.followup.send(
                f"Loi: `{e}`\n\nKiem tra bot co quyen Administrator "
                f"va role bot nam tren cung.",
                ephemeral=True,
            )

# ===== HÀM TẠO SERVER =====
async def build_server(guild: discord.Guild, count: int, user_names: list, description: str):
    text = description.lower()

    themes = {
        "gaming": r"game|gaming|lien quan|valorant|lol|minecraft|pubg|fps|esport",
        "study": r"hoc|study|school|truong|toan|ly|hoa|english|ielts|tai lieu",
        "community": r"cong dong|community|chung|chat|giao luu|ket ban",
        "music": r"nhac|music|am nhac|karaoke|beat",
        "art": r"ve|art|thiet ke|design|my thuat|draw",
        "tech": r"code|lap trinh|tech|cong nghe|dev|it",
    }

    theme_name = "community"
    for name, pattern in themes.items():
        if re.search(pattern, text):
            theme_name = name
            break

    presets = {
        "gaming": {
            "cats": ["🎮 Khu Vuc Gaming", "📢 Thong Tin", "💬 Cong Dong", "🎯 Leo Rank"],
            "channels": {
                "🎮 Khu Vuc Gaming": ["🎮-game-chung", "🔫-fps", "⚔️-moba", "🏆-giai-dau"],
                "📢 Thong Tin": ["📣-thong-bao", "📜-noi-quy", "🎉-su-kien"],
                "💬 Cong Dong": ["💬-tan-gau", "🖼️-media", "🤖-bot-commands"],
                "🎯 Leo Rank": ["🔍-tim-dong-doi", "📊-thanh-tich", "🎙️-rank-voice"],
            },
            "roles": ["Admin", "Moderator", "Gamer", "VIP", "Member"],
        },
        "study": {
            "cats": ["📚 Hoc Tap", "📢 Thong Tin", "💬 Thao Luan", "🎯 Luyen Tap"],
            "channels": {
                "📚 Hoc Tap": ["📖-tai-lieu", "🧮-toan", "🔬-khoa-hoc", "📝-tieng-anh"],
                "📢 Thong Tin": ["📣-thong-bao", "📜-noi-quy", "📅-lich-hoc"],
                "💬 Thao Luan": ["💬-hoi-dap", "🤝-study-together", "🤖-bot-commands"],
                "🎯 Luyen Tap": ["📝-bai-tap", "🏆-xep-hang", "🎙️-study-voice"],
            },
            "roles": ["Admin", "Moderator", "Hoc Vien", "Tro Giang", "Member"],
        },
        "community": {
            "cats": ["📢 Thong Tin", "💬 Tro Chuyen", "🎉 Giai Tri", "🔊 Voice Chat"],
            "channels": {
                "📢 Thong Tin": ["👋-chao-mung", "📣-thong-bao", "📜-noi-quy", "🎭-chon-role"],
                "💬 Tro Chuyen": ["💬-tong-hop", "🖼️-media", "😂-meme", "🤖-bot-commands"],
                "🎉 Giai Tri": ["🎵-am-nhac", "🎮-mini-game", "🎬-phim", "🎨-nghe-thuat"],
                "🔊 Voice Chat": ["🔊-voice-chung", "🎮-gaming-voice", "🎵-music-voice"],
            },
            "roles": ["Admin", "Moderator", "VIP", "Boosters", "Member"],
        },
    }

    preset = presets.get(theme_name, presets["community"])

    if user_names:
        cat_names = [
            f"{ICONS['category'][i % len(ICONS['category'])]} {n}"
            for i, n in enumerate(user_names[:count])
        ]
    else:
        cat_names = preset["cats"][:count]

    stats = {"categories": 0, "text_channels": 0, "voice_channels": 0, "roles": 0}

    for role_name in preset["roles"]:
        try:
            await guild.create_role(
                name=role_name,
                reason="DobbySetup Bot",
                colour=discord.Colour.random(),
            )
            stats["roles"] += 1
        except Exception as e:
            print(f"[ROLE ERROR] {role_name}: {e}")

    for cat_name in cat_names:
        try:
            category = await guild.create_category(
                name=cat_name,
                reason="DobbySetup Bot",
            )
            stats["categories"] += 1
        except Exception as e:
            print(f"[CAT ERROR] {cat_name}: {e}")
            continue

        preset_key = None
        for k in preset["channels"].keys():
            parts = k.split(" ")
            keyword = parts[1].lower() if len(parts) > 1 else None
            if keyword and keyword in cat_name.lower():
                preset_key = k
                break

        channel_list = preset["channels"].get(
            preset_key, ["💬-chung", "📌-thong-bao", "🤖-bot-commands"]
        )

        for ch_name in channel_list:
            is_voice = bool(re.search(r"voice|🎙️|🔊", ch_name))
            try:
                if is_voice:
                    await guild.create_voice_channel(
                        name=ch_name,
                        category=category,
                        reason="DobbySetup Bot",
                    )
                    stats["voice_channels"] += 1
                else:
                    await guild.create_text_channel(
                        name=ch_name,
                        category=category,
                        reason="DobbySetup Bot",
                    )
                    stats["text_channels"] += 1
            except Exception as e:
                print(f"[CH ERROR] {ch_name}: {e}")

    return stats

# ===== BOT =====
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ON READY - SYNC LỆNH =====
@bot.event
async def on_ready():
    print(f"===== BOT ONLINE: {bot.user} =====")
    print(f"===== GUILD_ID = {GUILD_ID} =====")
    await bot.wait_until_ready()
    print("===== BOT READY =====")

    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            print(f"===== SYNCING to guild {GUILD_ID} =====")

            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)
            print("===== CLEARED old commands =====")

            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"===== SYNCED {len(synced)} commands =====")
        else:
            print("===== NO GUILD_ID, SYNC GLOBAL =====")
            synced = await bot.tree.sync()
            print(f"===== SYNCED {len(synced)} commands global =====")
    except Exception as e:
        print(f"===== SYNC ERROR: {e} =====")

# ===== LỆNH /setup =====
@bot.tree.command(name="setup", description="Thiet lap server bang AI")
@app_commands.default_permissions(administrator=True)
async def setup_command(interaction: discord.Interaction):
    await interaction.response.send_modal(SetupModal())

# ===== WELCOME / GOODBYE =====
@bot.event
async def on_member_join(member: discord.Member):
    # Auto role
    try:
        for role in member.guild.roles:
            if role.name == "Member":
                await member.add_roles(role, reason="Auto role")
                break
    except Exception as e:
        print(f"[AUTO ROLE ERROR] {e}")

    # Welcome
    channel = None
    for c in member.guild.text_channels:
        if "chao-mung" in c.name.lower() or "welcome" in c.name.lower():
            channel = c
            break

    if channel:
        embed = discord.Embed(
            title=f"🎉 Chao mung {member.name}!",
            description=(
                f"{member.mention} vua tham gia **{member.guild.name}**!\n\n"
                f"> 👥 Ban la thanh vien thu **{member.guild.member_count}**\n"
                f"> 📜 Doc noi quy o kenh **noi-quy**\n"
                f"> 🎭 Chon role o kenh **chon-role**"
            ),
            color=0x57F287,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set
        
