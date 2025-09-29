import ctypes
import discord
from discord.ui import Button, Modal, TextInput, View
from discord import Interaction, Embed
from discord.ext import commands
import random
import json
import os
from typing import Dict, List
import datetime
from discord.ext import tasks
from cryptography.fernet import Fernet
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import asyncio
import time
from discord import ActivityType
from discord import FFmpegPCMAudio
from discord import VoiceClient
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands


ctypes.windll.kernel32.SetConsoleTitleW("Vale MM")

load_dotenv()
TOKEN: str = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No Discord bot token found. Check your .env file.")

# Constants for classes
CLASSES = ["Infantry", "Archer", "Cavalry"]
DEFAULT_ELO = 1500
K_FACTOR = 40  # ELO adjustment factor
ALLOWED_VOICE_CHANNEL_ID = 1327625178129104946  

# Haritalar ve medeniyetler
MAPS = [
    "Trading Post", "Xauna", "Echerion", "Town Outskirts", "Port At Omor",
    "Zendyar", "Vatnborg", "Sharis", "Lighthouse", "Abandoned", 
    "Ghost Town", "Lycaron Districts", "Fort of Honour", "Purple Haze", "Fort Lieve"
]

CIVILIZATIONS = [
    "Vlandiya", "Batanya", "Sturgiya", "Aseray", "Khuzait", "Empire"
]

emoji = {
    "Empire": "<:empire:1332358276977004626>",
    "Khuzait": "<:khuzait:1332358280692895946>",
    "Vlandiya": "<:vlandiya:1332358278956585071>",
    "Batanya": "<:batanya:1332358275018129561>",
    "Aseray": "<:aseray:1332358270756585606>",
    "Sturgiya": "<:sturgiya:1332358272769855643>"
}

map_image_urls = {
    "Trading Post": "https://media.discordapp.net/attachments/1163859458296909994/1332349936141996112/Trading-Post-frame-Aero.png?ex=6794ef12&is=67939d92&hm=a4fe34e1ad9dc8a6d7c9475071d7f02ba132b528ce2dd19a852e94e4f88f8961&=&format=webp&quality=lossless",
    "Xauna": "https://media.discordapp.net/attachments/1163859458296909994/1332349989640474624/Xuana-frame-Aero.png?ex=6794ef1f&is=67939d9f&hm=45c3475f8ddec134e7d4f10920befb3b2f7df3449ddac5f30ee3ab1d98f162a3&=&format=webp&quality=lossless",
    "Echerion": "https://media.discordapp.net/attachments/1163859458296909994/1332349620801769584/Echerion-frame-Aero.png?ex=6794eec7&is=67939d47&hm=8299ea10dc7bd6f8596b82b88c060112fb76e2c67cd808d3fb97b55739e3eb0c&=&format=webp&quality=lossless",
    "Town Outskirts": "https://media.discordapp.net/attachments/1163859458296909994/1332350162227695647/Town-Outskirts-frame-Aero.png?ex=67983b08&is=6796e988&hm=85a6c5b542770a4d63abf5bba24fbe9aa93eae742565be70a7af19b520f4c66e&=&format=webp&quality=lossless",
    "Port At Omor": "https://media.discordapp.net/attachments/1163859458296909994/1332349747922472993/Port-at-Omor-frame-Aero.png?ex=6794eee5&is=67939d65&hm=848b5268f322a2938e60971479483fd70b704d3578146418b51940f2ab2573a9&=&format=webp&quality=lossless",
    "Zendyar": "https://media.discordapp.net/attachments/1163859458296909994/1332349890323550369/zendyarheader.png?ex=6794ef07&is=67939d87&hm=bbbba9dd022aa7ba6f98a021d974bcf4daaf2e0bf300d640f0e6d826fba712df&=&format=webp&quality=lossless",
    "Vatnborg": "https://media.discordapp.net/attachments/1163859458296909994/1332349591013560364/Vatnborg_mm_preview.png?ex=6794eec0&is=67939d40&hm=3b0354eb614eba2c2c313b6d9622a0523b4ff26472f3136753aaf408c2d6a161&=&format=webp&quality=lossless",
    "Sharis": "https://media.discordapp.net/attachments/1163859458296909994/1332349850460622900/sharisheader.png?ex=6794eefe&is=67939d7e&hm=1dbfe536971e08e1b00098a6fde652d355134d0dff64bc877393b4506c8c70d2&=&format=webp&quality=lossless",
    "Lighthouse": "https://media.discordapp.net/attachments/1163859458296909994/1332349807737704468/Lighthouse_mm_preview.png?ex=6794eef4&is=67939d74&hm=d9c44f48d5d4e13d87b4b2ee040628f21831096d9a16f5ba071f8709215a0ecb&=&format=webp&quality=lossless",
    "Abandoned": "https://media.discordapp.net/attachments/1163859458296909994/1332349692285161492/abandoned_mm_preview.png?ex=6794eed8&is=67939d58&hm=0d812e75abf0c16800974903308a5befacde72e9fc041bf4e72f18f6859fd7c7&=&format=webp&quality=lossless",
    "Ghost Town": "https://media.discordapp.net/attachments/1163859458296909994/1332349543286575307/Ghosttown_mm_preview.png?ex=6794eeb4&is=67939d34&hm=29950de0c0a054aa9c0bf0ab5a5c559586f41f09253b30c0947b6d39ff34edbf&=&format=webp&quality=lossless",
    "Lycaron Districts": "https://media.discordapp.net/attachments/1163859458296909994/1332350255202828370/lc_mm_preview.png?ex=6794ef5e&is=67939dde&hm=95305f87f90c8f0270b8a71cd436fbd4a80dbe5b883836e846086eeb452ccb79&=&format=webp&quality=lossless",
    "Fort of Honour": "https://media.discordapp.net/attachments/1163859458296909994/1332350057927933973/Fortofhonour_mm_preview.png?ex=6794ef2f&is=67939daf&hm=bf160cef560510d6ef3098a409576046fcbe50a51b669db0f519368c1389fd97&=&format=webp&quality=lossless",
    "Purple Haze":"https://media.discordapp.net/attachments/1163859458296909994/1341414797622771732/purple_mm_preview.png?ex=67b5e962&is=67b497e2&hm=75e96be4d10ec0af99ce9a28217b146fb610e5974c1005b96153e329c095b21d&=&format=webp&quality=lossless&width=1440&height=641",
    "Fort Lieve": "https://media.discordapp.net/attachments/1163859458296909994/1341414909560356955/fortlieve_mm_preview.png?ex=67b5e97c&is=67b497fc&hm=a4e40dc3ad38fd5ca9b158ac3eff3a211720411e8bca2a72328422d6cda0bc2a&=&format=webp&quality=lossless&width=1440&height=641"
}

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# JSON file konumları
DATA_FOLDER = "data"
PLAYER_DATA_FILE = os.path.join(DATA_FOLDER, "player_data.json")
ELO_RATINGS_FILE = os.path.join(DATA_FOLDER, "elo_ratings.json")
GAME_ID_FILE = os.path.join(DATA_FOLDER, "game_ids.json")
BANS_FILE = os.path.join(DATA_FOLDER, "bans.json")
WARNS_FILE = os.path.join(DATA_FOLDER, "warns.json")
WINLOSE_FILE = os.path.join(DATA_FOLDER, "winloserate.json")

# Hedef sunucu ve ses kanalı
TARGET_GUILD_ID = 612197646920056832  # Hedef sunucunun ID'si
TARGET_CHANNEL_NAME = "Queue"         # Hedef ses kanalının adı

# Hedef ses kanalındaki kayıtlı oyuncuları tutmak için bir liste
registered_voice_members = []

bans = {}
warns = {}

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def save_data():
    """Save data to JSON files."""
    with open(PLAYER_DATA_FILE, "w") as f:
        json.dump(registered_players, f)
    with open(ELO_RATINGS_FILE, "w") as f:
        json.dump(elo_ratings, f) 

def load_data():
    """Load data from JSON files."""
    global registered_players, elo_ratings
    try:
        with open(PLAYER_DATA_FILE, "r") as f:
            registered_players = {int(k): v for k, v in json.load(f).items()} if os.path.getsize(PLAYER_DATA_FILE) > 0 else {}
        with open(ELO_RATINGS_FILE, "r") as f:
            elo_ratings = {int(k): v for k, v in json.load(f).items()} if os.path.getsize(ELO_RATINGS_FILE) > 0 else {}

    except FileNotFoundError:
        print("Data files not found. Initializing empty data.")
        registered_players = {}
        elo_ratings = {}

    except json.JSONDecodeError as e:
        print(f"Error loading JSON data: {e}")
        registered_players = {}
        elo_ratings = {}


def load_warns():
    """Warns JSON dosyasını yükler, eğer yoksa yenisini oluşturur."""
    try:
        with open(WARNS_FILE, "r") as f:
            global warns
            warns = json.load(f)
    except json.JSONDecodeError:
        warns = {}  # Eğer JSON bozuksa, boş bir sözlükle başlatır
        save_warns()  # Bozuk JSON'u sıfırlar

def load_bans():
    """Bans JSON dosyasını yükler, eğer yoksa yenisini oluşturur."""
    try:
        with open(BANS_FILE, "r") as f:
            global bans
            bans = json.load(f)
    except json.JSONDecodeError:
        bans = {}  # Eğer JSON bozuksa, boş bir sözlükle başlatır
        save_bans()  # Bozuk JSON'u sıfırlar

def save_warns():
    """Warns JSON dosyasına verileri kaydeder."""
    with open(WARNS_FILE, "w") as f:
        json.dump(warns, f, indent=4)

def save_bans():
    """Bans JSON dosyasına verileri kaydeder."""
    with open(BANS_FILE, "w") as f:
        json.dump(bans, f, indent=4)


registered_players: Dict[int, Dict[str, str]] = {}
elo_ratings: Dict[int, int] = {}

def load_game_id():
    if os.path.exists(GAME_ID_FILE):
        with open(GAME_ID_FILE, "r") as file:
            data = json.load(file)
            return data.get("current_game_id", 1)  # Varsayılan olarak 1 döndür
    else:
        return 1  # Dosya yoksa başlat

def save_game_id(game_id):
    with open(GAME_ID_FILE, "w") as file:
        json.dump({"current_game_id": game_id}, file)


current_game_id = load_game_id()


@tasks.loop(seconds=2)  # Her 5 saniyede bir kontrol
async def update_registered_voice_members():
    global registered_voice_members

    
    target_guild = discord.utils.get(bot.guilds, id=TARGET_GUILD_ID)
    if not target_guild:
        print(f"Hedef sunucu bulunamadı: {TARGET_GUILD_ID}")
        return

    # Hedef ses kanalını al
    target_channel = discord.utils.get(target_guild.voice_channels, name=TARGET_CHANNEL_NAME)
    if not target_channel:
        print(f"Hedef ses kanalı bulunamadı: {TARGET_CHANNEL_NAME}")
        return

    # Kanalda bulunan ve kayıtlı oyuncuları filtreler
    registered_voice_members = [
        member for member in target_channel.members if member.id in registered_players
    ]


OWNER_ID = 293023233555300352
def is_owner_or_role(*role_names):
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        if any(role.name in role_names for role in ctx.author.roles):
            return True
        await ctx.send("Bu komutu kullanmak için yetkiniz yok!")
        return False
    return commands.check(predicate)

from discord import Interaction
from discord import app_commands

def slash_is_owner_or_role(*role_names):
    async def predicate(interaction: Interaction):
        if interaction.user.id == OWNER_ID:
            return True
        if interaction.guild is None:
            return False  # DM'de çalışmasın
        user_roles = [role.name for role in interaction.user.roles]
        return any(role in role_names for role in user_roles)
    return app_commands.check(predicate)


# Belirli bir kanal için kayıtlı oyuncuları alma fonksiyonum
def get_registered_members():
    # Banlı oyuncuları JSON'dan çeker
    try:
        with open("bans.json", "r", encoding="utf-8") as f:
            banned_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        banned_data = {}

   
    current_time = time.time()

   
    active_bans = {int(user_id) for user_id, ban_info in banned_data.items() if ban_info["ban_until"] > current_time}

   
    return [member for member in registered_voice_members if member.id not in active_bans]

async def delete_all_messages(channel):
    try:
        
        if channel.permissions_for(channel.guild.me).manage_messages:
            
            async for message in channel.history(limit=100):  
                await message.delete()
        else:
            print("Botun mesajları silme yetkisi yok!")
    except discord.Forbidden:
        print("Botun mesajları silme yetkisi yok!")
    except discord.HTTPException as e:
        print(f"Mesajlar silinirken bir hata oluştu: {e}")


# Load data when bot starts
@bot.event
async def on_ready():
    load_data()  # Explicitly load data from JSON files
    bot.add_view(RegisterView())
    print(f"Bot {bot.user.name} is ready and online!")
    print(f"Loaded {len(registered_players)} players")
    print(f"Loaded {len(elo_ratings)} ELO ratings")
    update_registered_voice_members.start()
    auto_clean_bans.start()
    auto_clean_warns.start() 
    try:
        synced = await bot.tree.sync()
        print(f'Slash komutları senkronize edildi: {len(synced)} komut.')
    except Exception as e:
        print(f'Senkronizasyon hatası: {e}')
    
    await bot.change_presence(activity=discord.Activity(type=ActivityType.watching, name="discord.gg/thevale"), status=discord.Status.online)
    bot.temp_channels = []
    teams = {}

#register
class ClassRegistrationModal(Modal, title="Class Registration"):
    def __init__(self):
        super().__init__()

        # Main Class input
        self.main_class = TextInput(
            label="Main Class (Infantry / Archer / Cavalry)",
            placeholder="Infantry, Archer, or Cavalry tam ismini yazın",
            required=True,
            max_length=20
        )
        self.add_item(self.main_class)

        # Secondary Class input
        self.secondary_class = TextInput(
            label="Secondary Class (Infantry / Archer / Cavalry)",
            placeholder="Infantry, Archer, or Cavalry tam ismini yazın",
            required=True,
            max_length=20
        )
        self.add_item(self.secondary_class)

    async def on_submit(self, interaction: Interaction):
        # Kullanıcıdan alınan veriler
        main_class = self.main_class.value.strip().capitalize()
        secondary_class = self.secondary_class.value.strip().capitalize()

        # Aynı sınıf seçilirse hata mesajı
        if main_class == secondary_class:
            await interaction.response.send_message(
                "Main ve Secondary Class aynı olamaz! Lütfen farklı sınıflar seçin.",
                ephemeral=True
            )
            return

        # Geçerli sınıf kontrolü
        if main_class not in CLASSES or secondary_class not in CLASSES:
            await interaction.response.send_message(
                f"Geçersiz sınıf seçimi! Lütfen şunlardan birini seçin ve tam ismini yazın: {', '.join(CLASSES)}",
                ephemeral=True
            )
            return

        load_data()
        
        with open(PLAYER_DATA_FILE, "r") as f:
            player_data = {int(k): v for k, v in json.load(f).items()} if os.path.getsize(PLAYER_DATA_FILE) > 0 else {}

        
        if interaction.user.id in player_data:
            # Zaten kayıtlı ise, sadece main ve secondary class'ları güncelle
            player_data[interaction.user.id]["main"] = main_class
            player_data[interaction.user.id]["secondary"] = secondary_class

            # Mevcut ELO değerini koru
            current_elo = elo_ratings.get(interaction.user.id, DEFAULT_ELO)

            await interaction.response.send_message(
                f"Bilgileriniz güncellendi! Main Class: {main_class}, Secondary Class: {secondary_class}. Mevcut ELO: {current_elo}.",
                ephemeral=True
            )
        else:
            # Yeni kayıt işlemi
            player_data[interaction.user.id] = {
                "name": interaction.user.name,
                "main": main_class,
                "secondary": secondary_class,
                "elo": DEFAULT_ELO
            }
            elo_ratings[interaction.user.id] = DEFAULT_ELO

            await interaction.response.send_message(
                f"Kayıt tamamlandı! Main Class: {main_class}, Secondary Class: {secondary_class}.",
                ephemeral=True
            )

        #update json
        with open(PLAYER_DATA_FILE, "w") as f:
            json.dump(player_data, f)
        with open(ELO_RATINGS_FILE, "w") as f:
            json.dump(elo_ratings, f)


class RegisterView(View):
    def __init__(self):
        super().__init__(timeout=None)  # kalıcı butonlar için timeout = None

        # "Kayıt Ol" butonu
        self.register_button = Button(
            label="Kayıt Ol",
            style=discord.ButtonStyle.green,
            custom_id="register_button"
        )
        self.register_button.callback = self.open_modal
        self.add_item(self.register_button)

    async def open_modal(self, interaction: Interaction):
        """Kayıt formunu açar."""
        modal = ClassRegistrationModal()
        await interaction.response.send_modal(modal)
        

@bot.command()
@is_owner_or_role("First", "Mod")  # Bu iki role sahip olanlar kullanabilir. (bu isimle rol açabilirsiniz veya mevcut rolleri bu isime çevirin yada direkt koddaki isimi değiştirin)
async def register(ctx):
    """Kayıt formu mesajını gönderir."""
    embed = Embed(
        title="Class Seçim",
        description="- İstediğiniz main class'ı yazın. (infantry/archer/cavalry)\n\n- İstediğiniz secondary class'ı yazın. (infantry/archer/cavalry)\n\n- Gönder butonuna bastıktan sonra verileriniz kayıt edilecek ve 'QUEUE' odasında maça girebileceksiniz.\n\n- Class'larınızı değişmek istediğiniz zaman tekrardan butona basarak aynı işlemi tekrarlayın",
        color=discord.Color.green()
    )
    view = RegisterView()
    await ctx.send(embed=embed, view=view)




#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------


# Maçları tutacak liste
matches = []

def generate_random_match():

    map_choice = random.choice(MAPS)
    civ1, civ2 = random.sample(CIVILIZATIONS, 2)  # Farklı iki medeniyet
    return {"map": map_choice, "civilizations": [civ1, civ2]}


def refresh_matches():

    while len(matches) < 3:
        matches.append(generate_random_match())

async def run_match_logic(ctx, members, channel):

    with open(WINLOSE_FILE, "r", encoding="utf-8") as winlose_file:
        winlose_data = json.load(winlose_file)

    load_data()

    global teams 
    global bot

    
    # Tüm oyuncuları ELO'ya göre sıralar
    sorted_players = sorted(members, key=lambda m: elo_ratings[m.id], reverse=True)


    best_teams = None
    min_elo_difference = float('inf')

    # Oyuncuları tüm olası kombinasyonlarla kontrol et
    for i in range(1 << len(sorted_players)):
        team1 = []
        team2 = []
        for j in range(len(sorted_players)):
            if (i >> j) & 1:
                team1.append(sorted_players[j])
            else:
                team2.append(sorted_players[j])

        # Sadece 6'ya 6 olan kombinasyonlar
        if len(team1) == 6 and len(team2) == 6:
            team1_elo = sum(elo_ratings[member.id] for member in team1)
            team2_elo = sum(elo_ratings[member.id] for member in team2)
            elo_difference = abs(team1_elo - team2_elo)

            if elo_difference < min_elo_difference:
                min_elo_difference = elo_difference
                best_teams = (team1, team2)

    # En iyi takımları seç (ELO değerlerine göre en dengeli olacak)
    teams = {"team1": best_teams[0], "team2": best_teams[1]}

    # Takımları sınıflara göre ayır ve sınıf atamaları yap
    for team_name, team_members in teams.items():
        class_distribution = {"Infantry": 3, "Archer": 1, "Cavalry": 2}

        # Her oyuncunun sınıfı, takım için gerekli kontenjanı dolduracak şekilde atama.
        archer_count = 0
        cavalry_count = 0
        max_quota = {"Infantry": 3, "Archer": 1, "Cavalry": 2}

        for member in team_members:
            main_class = registered_players[member.id]["main"]
            secondary_class = registered_players[member.id]["secondary"]

            # Eğer main class dolmamışsa, ana sınıfa atama yap
            if main_class == "Infantry" and infantry_count < max_quota["Infantry"]:
                infantry_count += 1
            elif main_class == "Archer" and archer_count < max_quota["Archer"]:
                archer_count += 1
            elif main_class == "Cavalry" and cavalry_count < max_quota["Cavalry"]:
                cavalry_count += 1

            # Eğer main class doluysa, secondary class kontrolü
            else:
                if secondary_class == "Infantry" and infantry_count < max_quota["Infantry"]:
                    infantry_count += 1
                    registered_players[member.id]["main"] = "Infantry"  # Sınıf güncellenir
                elif secondary_class == "Archer" and archer_count < max_quota["Archer"]:
                    archer_count += 1
                    registered_players[member.id]["main"] = "Archer"
                elif secondary_class == "Cavalry" and cavalry_count < max_quota["Cavalry"]:
                    cavalry_count += 1
                    registered_players[member.id]["main"] = "Cavalry"

        # Eğer aynı main ve secondary class'a sahip birden fazla kişi varsa ELO'ya göre seçim yapılır (Elosu fazla olanı seçer)
        for class_type in ["Infantry", "Archer", "Cavalry"]:
            while len([m for m in team_members if registered_players[m.id]["main"] == class_type]) > max_quota[class_type]:
                candidates = [m for m in team_members if registered_players[m.id]["main"] == class_type]
                lowest_elo_member = min(candidates, key=lambda m: elo_ratings[m.id])

                # Secondary class'a atama yap
                secondary_class = registered_players[lowest_elo_member.id]["secondary"]
                if secondary_class == "Infantry" and infantry_count < max_quota["Infantry"]:
                    infantry_count += 1
                    registered_players[lowest_elo_member.id]["main"] = "Infantry"
                elif secondary_class == "Archer" and archer_count < max_quota["Archer"]:
                    archer_count += 1
                    registered_players[lowest_elo_member.id]["main"] = "Archer"
                elif secondary_class == "Cavalry" and cavalry_count < max_quota["Cavalry"]:
                    cavalry_count += 1
                    registered_players[lowest_elo_member.id]["main"] = "Cavalry"

                # Eğer hiçbir yere atanamazsa, rastgele bir sınıfa atanır 
                else:
                    available_classes = [cls for cls, count in zip(["Infantry", "Archer", "Cavalry"], [infantry_count, archer_count, cavalry_count]) if count < max_quota[cls]]
                    if available_classes:
                        new_class = available_classes[0]  # İlk uygun sınıf seçilir
                        registered_players[lowest_elo_member.id]["main"] = new_class
                        if new_class == "Infantry":
                            infantry_count += 1
                        elif new_class == "Archer":
                            archer_count += 1
                        elif new_class == "Cavalry":
                            cavalry_count += 1


    # Her takım için IGL'yi seç (en yüksek üç ELO'lu oyuncudan rastgele biri)
    team1_igl_candidates = sorted(teams["team1"], key=lambda m: elo_ratings[m.id], reverse=True)[:3]
    team2_igl_candidates = sorted(teams["team2"], key=lambda m: elo_ratings[m.id], reverse=True)[:3]
    team1_igl = random.choice(team1_igl_candidates)
    team2_igl = random.choice(team2_igl_candidates)

    # ELO farklarınınn hesaplaması
    team1_elo = sum(elo_ratings[member.id] for member in teams["team1"])
    team2_elo = sum(elo_ratings[member.id] for member in teams["team2"])
    elo_difference = abs(team1_elo - team2_elo)

    # Ses kanalları burada oluşturulur
    guild = ctx.guild
    team1_channel = await guild.create_voice_channel(f"Team {team1_igl.display_name}", category=channel.category)
    team2_channel = await guild.create_voice_channel(f"Team {team2_igl.display_name}", category=channel.category)

    #Oyuncuları ses kanallarına burada taşınır
    for member in teams["team1"]:
        try:
            await member.move_to(team1_channel)
        except discord.errors.NotFound:
            print(f"{member} kanalında değil, taşıma başarısız.")
        except discord.errors.Forbidden:
            print(f"{member} için kanalına taşınma izni yok.")
        except discord.errors.HTTPException as e:
            print(f"{member} taşıma sırasında bir hata oluştu: {e}")

    for member in teams["team2"]:
        try:
            await member.move_to(team2_channel)
        except discord.errors.NotFound:
            print(f"{member} kanalında değil, taşıma başarısız.")
        except discord.errors.Forbidden:
            print(f"{member} için kanalına taşınma izni yok.")
        except discord.errors.HTTPException as e:
            print(f"{member} taşıma sırasında bir hata oluştu: {e}")


    selected_map = matches[0]["map"]
    team1_civilization = matches[0]["civilizations"][0]
    team2_civilization = matches[0]["civilizations"][1]



    # Maç embedi
    embed = discord.Embed(
        title=f"{emoji[team1_civilization]} {team1_civilization} vs. {team2_civilization} {emoji[team2_civilization]}",
        description=f"**Harita:** {selected_map}\n\n**Maç başladı!** Harita: {matches[0]['map']} | Medeniyetler: {matches[0]['civilizations'][0]} vs {matches[0]['civilizations'][1]}",
        color=discord.Color.gold()
    )

    # IGLler
    embed.add_field(
        name="🧠 IGL'ler",
        value=(
            f"**{emoji[team1_civilization]} {team1_civilization} IGL:** {team1_igl.display_name} \n"
            f"**{emoji[team2_civilization]} {team2_civilization} IGL:** {team2_igl.display_name} "
        ),
        inline=False
    )

    # Takım 1 detayları
    embed.add_field(
        name=f" --------------------- **{emoji[team1_civilization]} {team1_civilization} {emoji[team1_civilization]}** --------------------- ",
        value="Takım Detayları:",
        inline=False
    )

    for member in teams["team1"]:
        main_class = registered_players[member.id]["main"]
        played_matches = winlose_data.get(str(member.id), {}).get("played", 0)
        
        if played_matches < 5:
            elo_display = "Calibration"
        else:
            elo_display = elo_ratings[member.id]

        embed.add_field(
            name=f"{member.display_name}",
            value=f"{main_class}\n{elo_display}",
            inline=True
        )

    # Takım 2 detayları
    embed.add_field(
        name=f" --------------------- **{emoji[team2_civilization]} {team2_civilization} {emoji[team2_civilization]}** --------------------- ",
        value="Takım Detayları:",
        inline=False
    )

    for member in teams["team2"]:
        main_class = registered_players[member.id]["main"]
        played_matches = winlose_data.get(str(member.id), {}).get("played", 0)
        
        if played_matches < 5:
            elo_display = "Calibration"
        else:
            elo_display = elo_ratings[member.id]

        embed.add_field(
            name=f"{member.display_name}",
            value=f"{main_class}\n{elo_display}",
            inline=True
        )

    # Harita görseli
    map_image_url = map_image_urls.get(selected_map, None)
    if map_image_url:
        embed.set_image(url=map_image_url)

    
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")  # Örneğin: 24.01.2025
    embed.set_footer(text=f"GAMEID:{current_game_id} | ELO DIFF {elo_difference} | Maç tarihi: {current_date}")

    # Embed'i burda gönderir
    await ctx.send(embed=embed)

    # Geçici kanalların tutaruz silinmek üzere
    bot.temp_channels = [team1_channel, team2_channel]

   
    bot.current_teams = teams

    
    # İlk maçı kaldırır ve yeni bir maç ekler (gelecek maç listesinden)
    matches.pop(0)
    matches.append(generate_random_match())



async def send_start_button(ctx, members ,channel):
    refresh_matches()

    class StartMatchButton(Button):
        def __init__(self):
            super().__init__(label="Maçı Başlat", style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            allowed_roles = ["First", "Mod", "House Arryn"]  # Yetkili roller
            if not any(role.name in allowed_roles for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("Bu butona basma yetkiniz yok!", ephemeral=True)
                return
            if interaction.user.voice and interaction.user.voice.channel == channel:
                # Güncel kayıtlı oyuncuları kontrolü
                members = get_registered_members()

               
                if len(members) < 12:
                    await interaction.response.send_message(
                        f"🔴 Maçı başlatabilmek için ses kanalında en az 12 kayıtlı ve aktif banı olmayan oyuncu bulunmalı! Şu anda mevcut: {len(members)}",
                        ephemeral=True
                    )
                    return

                
                if len(members) > 12:
                    members = random.sample(members, 12)

                
                await interaction.message.delete()

                await interaction.response.send_message(f"Maç başlatılıyor... Oyuncu sayısı: {len(members)}", ephemeral=True)

                await run_match_logic(ctx, members, channel)

                await send_start_button(ctx, members ,channel)
            else:
                await interaction.response.send_message(
                    "Maç başlatmak için izinli ses kanalında olmalısınız.", ephemeral=True
                )

    async def handle_reaction_logic(message):
        """Tepkime sayısını kontrol eder ve maçları günceller."""
        reaction_counts = {0: 0}  

        def check_reaction(reaction, user):
            """Tepkileri kontrol et (bot dahil)."""
            return (
                str(reaction.emoji) == "❌"
                and reaction.message.id == message.id
            )

        while True:
            reaction, user = await bot.wait_for("reaction_add", check=check_reaction)

            # İlk maça tepkiyi artır
            reaction_counts[0] += 1  

            if reaction_counts[0] >= 6:  # 7 tepkiye ulaşıldıysa
                if matches:
                    # En üstteki maçı kaldırır ve yenisini ekler
                    skipped_match = matches.pop(0)
                    matches.append(generate_random_match())
                    reaction_counts[0] = 0  # Sayaç sıfırlar

                
                match_descriptions = [
                    "{}. Harita: {} | Medeniyetler: {} {} vs {} {}".format(
                        i + 1,
                        match["map"],
                        emoji.get(match["civilizations"][0], ""),
                        match["civilizations"][0],
                        emoji.get(match["civilizations"][1], ""),
                        match["civilizations"][1]
                    )
                    for i, match in enumerate(matches)
                ]

                
                await message.delete()
                view = View(timeout=None)
                view.add_item(StartMatchButton())
                new_message = await ctx.send(
                    "Güncellenen maç listesi:\n" + "\n".join(match_descriptions),
                    view=view
                )
                await new_message.add_reaction("❌")  
                message = new_message  

    
    view = View(timeout=None)
    view.add_item(StartMatchButton())

    match_descriptions = [
        "{}. Harita: {} | Medeniyetler: {}{} vs {}{}".format(
            i + 1,
            match["map"],
            emoji.get(match["civilizations"][0], ""),  # İlk medeniyetin emojisi
            match["civilizations"][0],                # İlk medeniyet adı
            emoji.get(match["civilizations"][1], ""),  # İkinci medeniyetin emojisi
            match["civilizations"][1]                 # İkinci medeniyet adı
        ) 
        for i, match in enumerate(matches)
        if len(match["civilizations"]) == 2  
    ]
    match_message = await ctx.send(
        "Maçı başlatmak için aşağıdaki butona tıklayın. İstemediğiniz maçı atlamak için toplam 7 ❌ tepkisi gereklidir:\n" + "\n".join(match_descriptions),
        view=view
    )

    await match_message.add_reaction("❌")  
    await handle_reaction_logic(match_message)


# START MATCH
@bot.command()
@is_owner_or_role("First", "Mod")
async def startmatch(ctx):
    allowed_channel_name = "Queue"

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("Maç başlatabilmek için ses kanalında olmalısın!")
        return

    channel = ctx.author.voice.channel
    if channel.name != allowed_channel_name:
        await ctx.send(f"{ctx.author.mention} Maçı sadece izin verilen kanalda başlatabilirsiniz: '{allowed_channel_name}'")
        return

    
    members = [member for member in channel.members if member.id in registered_players]

    
    if len(members) < 1:
        await ctx.send(f"Maçı başlatabilmek için ses kanalında en az 12 kayıtlı oyuncu bulunmalı! Şu anda mevcut: {len(members)}")
        return

    
    if len(members) > 12:
        members = random.sample(members, 12)

    
    await send_start_button(ctx, members, channel)


# maçın bitip bitmediğini kontrol etmek için global değişken
match_ended = False

@bot.event
async def on_voice_state_update(member, before, after):
    global match_ended

    for channel in bot.temp_channels:
        if len(channel.members) == 0 and match_ended:
            try:
                await channel.delete()
                bot.temp_channels.remove(channel)  
                print(f"{channel.name} silindi.")
            except Exception as e:
                print(f"Kanal silinirken hata oluştu: {e}")


calibration_threshold = 5  # Kalibrasyon için gereken maç sayısı
calibration_elo_map = {5: 1800, 4: 1700, 3: 1600, 2: 1500, 1: 1400, 0: 1300}

@bot.command()
@is_owner_or_role("First", "Mod")
async def endmatch(ctx, winning_team: str, winning_score: int, losing_score: int):
    global teams, match_ended

    if winning_team not in ["team1", "team2", "draw"]:
        await ctx.send(f"{ctx.author.mention} Geçersiz takım adı! 'team1', 'team2' veya 'draw' yazmalısınız.")
        return

    if 'teams' not in globals() or not teams or not teams.get("team1") or not teams.get("team2"):
        await ctx.send(f"{ctx.author.mention} Bitirilecek aktif maç bulunamadı!")
        return

    with open(WINLOSE_FILE, "r", encoding="utf-8") as winlose_file:
        winlose_data = json.load(winlose_file)

    with open(ELO_RATINGS_FILE, "r", encoding="utf-8") as elo_file:
        elo_ratings = json.load(elo_file)

    for team in ["team1", "team2"]:
        for member in teams[team]:
            member_id = str(member.id)
            if member_id not in winlose_data:
                winlose_data[member_id] = {"win": 0, "lose": 0, "played": 0}
            if member_id not in elo_ratings:
                elo_ratings[member_id] = 1500  #default elo 1500

    # Beraberlik durumu
    if winning_team == "draw":
        if winning_score != losing_score:
            await ctx.send(f"{ctx.author.mention} Beraberlik için skorlar eşit olmalıdır!")
            return

        for member in teams["team1"] + teams["team2"]:
            member_id = str(member.id)
            winlose_data[member_id]["played"] += 1

        
            
            if winlose_data[member_id]["played"] == calibration_threshold:
                wins = winlose_data[member_id]["win"]
                elo_ratings[member_id] = calibration_elo_map.get(wins, 1300)

        
        with open(WINLOSE_FILE, "w", encoding="utf-8") as winlose_file:
            json.dump(winlose_data, winlose_file, ensure_ascii=False, indent=4)

        with open(ELO_RATINGS_FILE, "w", encoding="utf-8") as elo_file:
            json.dump(elo_ratings, elo_file, ensure_ascii=False, indent=4)

        await ctx.send(f"Maç berabere bitti! Skor: {winning_score}-{losing_score}. ELO değişmedi.")
    
    else:
        # Skor kontrolü
        score_difference = winning_score - losing_score
        if score_difference <= 0:
            await ctx.send(f"{ctx.author.mention} Kazanan takımın skoru daha yüksek olmalı!")
            return

        elo_change = (score_difference * 6) + 8
        win_team = "team1" if winning_team == "team1" else "team2"
        lose_team = "team2" if winning_team == "team1" else "team1"

        
        for team, is_winner in [(win_team, True), (lose_team, False)]:
            for member in teams[team]:
                member_id = str(member.id)

                
                if is_winner:
                    winlose_data[member_id]["win"] += 1
                else:
                    winlose_data[member_id]["lose"] += 1
                
                winlose_data[member_id]["played"] += 1

                
                if winlose_data[member_id]["played"] == calibration_threshold:
                    wins = winlose_data[member_id]["win"]
                    elo_ratings[member_id] = calibration_elo_map.get(wins, 1300)
                elif winlose_data[member_id]["played"] > calibration_threshold:
                    elo_ratings[member_id] += elo_change if is_winner else -elo_change

        
        with open(WINLOSE_FILE, "w", encoding="utf-8") as winlose_file:
            json.dump(winlose_data, winlose_file, ensure_ascii=False, indent=4)

        with open(ELO_RATINGS_FILE, "w", encoding="utf-8") as elo_file:
            json.dump(elo_ratings, elo_file, ensure_ascii=False, indent=4)

        await ctx.send(f"Maç {ctx.author.mention} tarafından bitirildi! Skor: {winning_score}-{losing_score}.")

    
    match_ended = True

    # ses kanalları oyuncular sesten çıkınca otomatik olarak silinir
    await ctx.send("Maç sonlandırıldı. Ses kanalları, boşaldığında otomatik olarak silinecektir.")

    teams = {}


banlog_channel_id = 1345760369980997764


@bot.command()
@is_owner_or_role("First")  # Sadece "First" rolüne sahip olanlar kullanabilir
async def mmban(ctx, member: discord.Member, duration: str, *, reason="Sebep belirtilmedi"):
    try:
        # Ban süresi
        unit = duration[-1]  # Süre birimi (s, m, h, d)
        amount = int(duration[:-1])  
        
        time_multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if unit not in time_multiplier:
            await ctx.send("Geçersiz süre formatı! Örnek: 10m (10 dakika), 2h (2 saat), 1d (1 gün)")
            return

        ban_duration = amount * time_multiplier[unit]
        ban_until = time.time() + ban_duration  # Banın biteceği zaman
        unban_time = datetime.datetime.fromtimestamp(ban_until).strftime('%d.%m.%Y %H:%M')

        load_bans()  

        
        bans[str(member.id)] = {"ban_until": ban_until, "reason": reason}

        save_bans()  

        # Embed mesajı 
        embed = discord.Embed(description=f"🔴 **Ban**\n{member.mention} tarihine kadar banlandı **{unban_time}**\n**Sebep:** {reason}", 
                              color=discord.Color.red())

        log_channel = ctx.guild.get_channel(banlog_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

    except ValueError:
        await ctx.send("Geçersiz süre formatı! Örnek: 10m (10 dakika), 2h (2 saat), 1d (1 gün)")
    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")


@bot.command()
@is_owner_or_role("First")  # Sadece "First" rolüne sahip olanlar kullanabilir
async def mmwarn(ctx, member: discord.Member, count: int, duration: str, *, reason="Sebep belirtilmedi"):
    """Bir oyuncuya süreli uyarı verir."""
    try:
        # Süreyi hesapla
        unit = duration[-1]  # Süre birimi (s, m, h, d)
        amount = int(duration[:-1]) 
        
        time_multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if unit not in time_multiplier:
            await ctx.send("Geçersiz süre formatı! Örnek: 10m (10 dakika), 2h (2 saat), 1d (1 gün)")
            return

        warn_duration = amount * time_multiplier[unit]
        warn_until = time.time() + warn_duration  # Uyarının bitiş zamanı
        warn_time = datetime.datetime.fromtimestamp(warn_until).strftime('%d.%m.%Y %H:%M')

        load_warns()  

        user_id = str(member.id)
        if user_id not in warns:
            warns[user_id] = {"warnings": []}

        for i in range(count):  
            warns[user_id]["warnings"].append({
                "reason": reason,
                "warn_until": warn_until
            })

        save_warns()  

        total_warnings = len(warns[user_id]["warnings"])

        # Embed mesajı
        embed = discord.Embed(description=f"⚠️ **Uyarı**\n{member.mention} tarihine kadar uyarıldı **{warn_time}** (uyarı ağırlığı: {count})\n**Sebep:** {reason}\n**Toplam Uyarı:** {total_warnings}", 
                              color=discord.Color.gold())

        log_channel = ctx.guild.get_channel(banlog_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

    except ValueError:
        await ctx.send("Geçersiz süre formatı! Örnek: 10m (10 dakika), 2h (2 saat), 1d (1 gün)")
    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")





@bot.command()
@is_owner_or_role("First")  # Sadece "First" rolüne sahip olanlar kullanabilir
async def mmunwarn(ctx, member: discord.Member, count: int):
    """Bir oyuncunun uyarısını siler."""
    try:
        load_warns() 

        user_id = str(member.id)
        if user_id not in warns or len(warns[user_id]["warnings"]) < count:
            await ctx.send(f"{member.mention} adlı oyuncunun uyarısı bulunmuyor!")
            return

        del warns[user_id]["warnings"][count - 1]

        save_warns()

        # Embed mesajı
        embed = discord.Embed(description=f"🟢 **Uyarı Silindi**\n{member.mention} adlı oyuncudan {count} adet uyarı silindi.",
                              color=discord.Color.green())

        log_channel = ctx.guild.get_channel(banlog_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")



@bot.command()
@is_owner_or_role("First")  # Sadece "First" rolüne sahip olanlar kullanabilir
async def mmunban(ctx, member: discord.Member):
    """Bir oyuncunun banını kaldırır."""
    try:
        load_bans() 

        user_id = str(member.id)

        if user_id not in bans:
            await ctx.send(f"{member.mention} adlı oyuncu zaten banlanmamış!")
            return

        del bans[user_id]

        with open("bans.json", "w", encoding="utf-8") as f:
            json.dump(bans, f, indent=4)

        # Embed mesajı
        embed = discord.Embed(description=f"🟢 **Ban Kaldırıldı**\n{member.mention} adlı oyuncunun banı kaldırıldı.",
                              color=discord.Color.green())

        log_channel = ctx.guild.get_channel(banlog_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)


    except Exception as e:
        await ctx.send(f"Bir hata oluştu: {e}")


# Bilinmeyen hatalarda
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(f"{ctx.author.mention}, bu komutu kullanabilmek için gerekli izinlere sahip değilsiniz!")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, bu komutu kullanabilmek için gerekli izinlere sahip değilsiniz!")
    else:
        raise error


@bot.command()
@is_owner_or_role("First", "Mod")  # Bu iki role sahip olanlar kullanabilir
async def cancelmatch(ctx):
    """Mevcut maçı iptal et ve geçici kanalların otomatik silinmesini sağla."""
    global teams, match_ended  


    if 'teams' not in globals() or not teams or not teams.get("team1") or not teams.get("team2"):
        await ctx.send(f" {ctx.author.mention} İptal edilecek aktif bir maç bulunamadı! ")
        return

    match_ended = True

    await ctx.send(f"Maç {ctx.author.mention} isimli Moderator tarafından iptal edildi! ELO'larda değişiklik yapılmadı. Geçici kanallar kısa süre içinde silinecek.")

    teams = {}

    print("Maç iptal edildi ve geçici kanallar silinmek üzere işaretlendi.")



@bot.command()
async def stats(ctx):
    """Komutu kullanan kullanıcının istatistiklerini sunucudaki takma adıyla gösterir ve onu etiketler."""
    user_id = str(ctx.author.id)
    nickname = ctx.author.display_name
    mention = ctx.author.mention

    if not os.path.exists(PLAYER_DATA_FILE) or not os.path.exists(ELO_RATINGS_FILE) or not os.path.exists(WINLOSE_FILE):
        await ctx.send("Veri dosyaları bulunamadı. Lütfen yöneticinize bildirin.")
        return

    with open(PLAYER_DATA_FILE, "r", encoding="utf-8") as player_file:
        player_data = json.load(player_file)

    with open(ELO_RATINGS_FILE, "r", encoding="utf-8") as elo_file:
        elo_ratings = json.load(elo_file)

    with open(WINLOSE_FILE, "r", encoding="utf-8") as winlose_file:
        winlose_data = json.load(winlose_file)

    if user_id not in player_data:
        await ctx.send(f"{mention}, henüz istatistikleriniz kayıtlı değil! Kayıt olmak için lütfen class seç odasını kullanın.")
        return

    user_info = player_data[user_id]
    win = winlose_data.get(user_id, {}).get("win", 0)
    lose = winlose_data.get(user_id, {}).get("lose", 0)
    played = winlose_data.get(user_id, {}).get("played", 0)

    if played < 5:
        elo_display = "Calibration"
    else:
        elo_display = elo_ratings.get(user_id, DEFAULT_ELO)

    embed = discord.Embed(
        title=f"{nickname} - İstatistikler",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Main Class", value=user_info["main"], inline=False)
    embed.add_field(name="Secondary Class", value=user_info["secondary"], inline=False)
    embed.add_field(name="MMR", value=elo_display, inline=False)
    
    embed.add_field(
        name="Match Stats", 
        value=f"Wins: {win}\nLosses: {lose}\nMatches Played: {played}", 
        inline=False
    )

    await ctx.send(content=f"{mention}, işte istatistikleriniz:", embed=embed)

@bot.command()
async def top(ctx):
    """En yüksek ELO'ya sahip 10 oyuncuyu gösterir."""
    if not os.path.exists(PLAYER_DATA_FILE) or not os.path.exists(ELO_RATINGS_FILE) or not os.path.exists(WINLOSE_FILE):
        await ctx.send("Veri dosyaları bulunamadı. Lütfen yöneticinize bildirin.")
        return

    with open(PLAYER_DATA_FILE, "r", encoding="utf-8") as player_file:
        player_data = json.load(player_file)

    with open(ELO_RATINGS_FILE, "r", encoding="utf-8") as elo_file:
        elo_ratings = json.load(elo_file)

    with open(WINLOSE_FILE, "r", encoding="utf-8") as winlose_file:
        winlose_data = json.load(winlose_file)

    sorted_players = sorted(
        elo_ratings.items(),
        key=lambda x: x[1],  # ELO puanına göre sıralama
        reverse=True  # En yüksekten en düşüğe
    )

    # İlk 10 oyuncu
    top_players = sorted_players[:10]

    embed = discord.Embed(
        title="Liderlik Tablosu",
        description="En yüksek MMR'a sahip oyuncular",
        color=discord.Color.gold()
    )

    if not top_players:
        embed.description = "Henüz liderlik tablosunda gösterilecek oyuncu yok."
    else:
        for rank, (player_id, elo) in enumerate(top_players, start=1):
            player_name = player_data.get(player_id, {}).get("name", "Bilinmiyor")  # Kullanıcı adı
            main_class = player_data.get(player_id, {}).get("main", "Bilinmiyor")  # Ana class

            user = ctx.guild.get_member(int(player_id))
            nickname = user.display_name if user else "Unknown"

            # Win, Lose, Played verileri
            win = winlose_data.get(player_id, {}).get("win", 0)
            lose = winlose_data.get(player_id, {}).get("lose", 0)
            played = winlose_data.get(player_id, {}).get("played", 0)

            # Eğer oyuncu 5 maçtan az oynadıysa ELO yerine "Calibration" gösterir
            if played < 5:
                elo_display = "Calibration"
            else:
                elo_display = elo  # Gerçek ELO değeri

            # Embed'e ekle
            embed.add_field(
                name=f"#{rank} - {nickname}", 
                value=f"MMR: {elo_display}\nAna Class: {main_class}\nWins: {win}\nLosses: {lose}\nMatches Played: {played}",
                inline=False
            )

    await ctx.send(embed=embed)



@bot.command()
async def yardım(ctx):
    message = """ ```

    - !yardım = mevcut komutlari gösterir.
    - !register = kayıt olma mesajını atar (admin komutu)
    - !startmatch = haritaları atar
    - !endmatch <winning_team> <skor> = Kazanan takımı belirler 
    örnek kullanım: !endmatch team1 4 3 (admin komutu)(beraberlik için draw yazın) 
    - !cancelmatch = Maçı iptal eder (admin komutu)
    - !playerstats = Komutu kullanan oyuncunun istatistiklerini gösterir.
    - !top = en yüksek 10 MMR sahibinin istatistiklerini gösterir.
    
    ```"""
    await ctx.send(message) 



#süresi dolan banların ve uyarıların otomatik silinmesi
def clean_expired_bans():
    try:
        with open("bans.json", "r", encoding="utf-8") as f:
            bans = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bans = {}

    current_time = time.time()
    updated_bans = {user_id: data for user_id, data in bans.items() if data["ban_until"] > current_time}

    if len(updated_bans) != len(bans):
        with open("bans.json", "w", encoding="utf-8") as f:
            json.dump(updated_bans, f, indent=4)

@tasks.loop(minutes=10) 
async def auto_clean_bans():
    clean_expired_bans()


def clean_expired_warns():
    try:
        with open("warns.json", "r", encoding="utf-8") as f:
            warns = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        warns = {}

    current_time = time.time()

    updated_warns = {}
    
    for user_id, data in warns.items():
        active_warnings = [warn for warn in data["warnings"] if warn["warn_until"] > current_time]

        if active_warnings:
            updated_warns[user_id] = {
                "warnings": active_warnings,
                "count": len(active_warnings)  
            }

    if len(updated_warns) != len(warns):
        with open("warns.json", "w", encoding="utf-8") as f:
            json.dump(updated_warns, f, indent=4)

@tasks.loop(minutes=10)  # Her 10 dakikada bir kontrol
async def auto_clean_warns():
    clean_expired_warns()


TOKEN = TOKEN
bot.run(TOKEN)

