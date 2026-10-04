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
        self.wfile.write("Bot is alive! 🤖".encode("utf-8"))

    def log_message(self, format, *args):
        pass

def run_http_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"🌐 HTTP server đang chạy tại port {PORT}")
    server.serve_forever()

# ===== ICON & FONT ĐẸP =====
ICONS = {
    "category": ["📢", "💬", "🎮", "📚", "🎨", "🛠️", "🎉", "💼", "🌐"],
    "announce": ["📣", "🔔", "📢"],
}

def fancy(text: str) -> str:
    mapping = {}
    for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"):
        mapping[c] = chr(0x1D41A + i)
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        mapping[c] = chr(0x1D400 + i)
    return "".join(mapping.get(ch, ch) for ch in text)

def small_caps(text: str) -> str:
    return re.sub(r"[a-z]", lambda m: chr(ord(m.group()) + 0x1D00), text)

# ===== MODAL NHẬP LIỆU =====
class SetupModal(discord.ui.Modal, title="Thiết lập server bằng AI"):
    category_count = discord.ui.TextInput(
        label="Số lượng category muốn tạo",
        placeholder="Nhập số lượng danh mục muốn tạo, tối đa 9",
        required=True,
        max_length=1,
    )
    category_names = discord.ui.TextInput(
        label="Tên category (không bắt buộc)",
        placeholder="Ví dụ: Chào mừng, Chung, Giải trí...",
        required=False,
        max_length=200,
    )
    description = discord.ui.TextInput(
        label="Nhập yêu cầu của bạn",
        placeholder="Mô tả server bạn muốn (chủ đề, có kênh gì, quy mô cộng đồng...)",
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
                title=f"{fancy('Setup Server Complete')} ✨",
                description=(
                    f"{ICONS['announce'][0]} **Đã thiết lập server thành công!**\n\n"
                    f"> 📁 **Category:** `{stats['categories']}`\n"
                    f"> 💬 **Text Channels:** `{stats['text_channels']}`\n"
                    f"> 🔊 **Voice Channels:** `{stats['voice_channels']}`\n"
                    f"> 🎭 **Roles:** `{stats['roles']}`\n\n"
                    f"*{small_caps('Chuc ban quan ly server vui ve!')}*"
                ),
                color=0x5865F2,
            )
            embed.set_footer(
                text="Powered by AI Setup Bot",
                icon_url=interaction.client.user.display_avatar.url,
            )
            embed.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"❌ Lỗi build server: {e}")
            await interaction.followup.send(
                f"❌ Lỗi: `{e}`\n\n💡 **Gợi ý:** Kiểm tra bot có quyền Administrator "
                f"và role bot nằm trên cùng.",
                ephemeral=True,
            )

# ===== HÀM TẠO SERVER =====
async def build_server(guild: discord.Guild, count: int, user_names: list, description: str):
    text = description.lower()

    themes = {
        "gaming": r"game|gaming|liên quân|valorant|lol|minecraft|pubg|fps|esport",
        "study": r"học|study|school|trường|toán|lý|hóa|english|ielts|tài liệu",
        "community": r"cộng đồng|community|chung|chat|giao lưu|kết bạn",
        "music": r"nhạc|music|âm nhạc|karaoke|beat",
        "art": r"vẽ|art|thiết kế|design|mỹ thuật|draw",
        "tech": r"code|lập trình|tech|công nghệ|dev|it",
    }

    theme_name = "community"
    for name, pattern in themes.items():
        if re.search(pattern, text):
            theme_name = name
            break

    presets = {
        "gaming": {
            "cats": ["🎮 Khu Vực Gaming", "📢 Thông Tin", "💬 Cộng Đồng", "🎯 Leo Rank"],
            "channels": {
                "🎮 Khu Vực Gaming": ["🎮-game-chung", "🔫-fps", "⚔️-moba", "🏆-giải-đấu"],
                "📢 Thông Tin": ["📣-thông-báo", "📜-nội-quy", "🎉-sự-kiện"],
                "💬 Cộng Đồng": ["💬-tán-gẫu", "🖼️-media", "🤖-bot-commands"],
                "🎯 Leo Rank": ["🔍-tìm-đồng-đội", "📊-thành-tích", "🎙️-rank-voice"],
            },
            "roles": ["👑 Admin", "🛡️ Moderator", "🎮 Gamer", "⭐ VIP", "👤 Member"],
        },
        "study": {
            "cats": ["📚 Học Tập", "📢 Thông Tin", "💬 Thảo Luận", "🎯 Luyện Tập"],
            "channels": {
                "📚 Học Tập": ["📖-tài-liệu", "🧮-toán", "🔬-khoa-học", "📝-tiếng-anh"],
                "📢 Thông Tin": ["📣-thông-báo", "📜-nội-quy", "📅-lịch-học"],
                "💬 Thảo Luận": ["💬-hỏi-đáp", "🤝-study-together", "🤖-bot-commands"],
                "🎯 Luyện Tập": ["📝-bài-tập", "🏆-xếp-hạng", "🎙️-study-voice"],
            },
            "roles": ["👑 Admin", "🛡️ Moderator", "🎓 Học Viên", "⭐ Trợ Giảng", "👤 Member"],
        },
        "community": {
            "cats": ["📢 Thông Tin",👤 "💬 Trò Chuyện", "🎉 Giải Trí", "🔊 Voice Chat"],
            "channels": {
                " Member📢 Thông Tin": ["👋-chào-mừng", "📣-thông-báo", "📜-n"],
ội-quy", "🎭-chọn-role"],
                "💬 Trò Chuyện": ["💬-tổ       ng-hợp", "🖼️-media", "😂-meme", "🤖-bot-commands"],
                "🎉 Giải Trí": ["🎵 },
-âm-nhạc", "🎮-mini-game", "🎬-phim", "🎨-nghệ-thuật"],
                   "🔊 Voice Chat": ["🔊-voice-chung", "🎮-gaming-voice", "🎵-music-voice"],
            },
            "roles": ["👑 Admin", "🛡️ Moderator", "⭐ VIP", "💎 Boosters", " }

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
                reason="AI Setup Bot",
                colour=discord.Colour.random(),
            )
            stats["roles"] += 1
        except Exception as e:
            print(f"⚠️ Không tạo được role {role_name}: {e}")

    for cat_name in cat_names:
        try:
            category = await guild.create_category(
                name=cat_name,
                reason="AI Setup Bot",
            )
            stats["categories"] += 1
        except Exception as e:
            print(f"⚠️ Không tạo được category {cat_name}: {e}")
            continue

        preset_key = None
        for k in preset["channels"].keys():
            parts = k.split(" ")
            keyword = parts[1].lower() if len(parts) > 1 else None
            if keyword and keyword in cat_name.lower():
                preset_key = k
                break

        channel_list = preset["channels"].get(
            preset_key, ["💬-chung", "📌-thông-báo", "🤖-bot-commands"]
        )

        for ch_name in channel_list:
            is_voice = bool(re.search(r"voice|🎙️|🔊", ch_name))
            try:
                if is_voice:
                    await guild.create_voice_channel(
                        name=ch_name,
                        category=category,
                        reason="AI Setup Bot",
                    )
                    stats["voice_channels"] += 1
                else:
                    await guild.create_text_channel(
                        name=ch_name,
                        category=category,
                        reason="AI Setup Bot",
                    )
                    stats["text_channels"] += 1
            except Exception as e:
                print(f"⚠️ Không tạo được channel {ch_name}: {e}")

    return stats

# ===== BOT SETUP =====
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"✅ Đã sync {len(synced)} command vào guild {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"✅ Đã sync {len(synced)} command toàn cầu")
    except Exception as e:
        print(f"❌ Lỗi sync command: {e}")

@bot.tree.command(name="setup", description="Thiết lập server bằng AI")
@app_commands.default_permissions(administrator=True)
async def setup_command(interaction: discord.Interaction):
    await interaction.response.send_modal(SetupModal())

@bot.event
async def on_member_join(member: discord.Member):
    try:
        for role in member.guild.roles:
            if "Member" in role.name or "Thành viên" in role.name:
                await member.add_roles(role, reason="Auto role")
                break
    except Exception as e:
        print(f"⚠️ Không thể auto-role: {e}")

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=run_http_server, daemon=True).start()
    bot.run(TOKEN)
  
