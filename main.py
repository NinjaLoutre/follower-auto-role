import discord
import requests
import os
import asyncio

# === CONFIGURATION ===
TWITCH_CLIENT_ID = "29hnvf3ru8waz788a3yqfaxyb67krw"
TWITCH_ACCESS_TOKEN = "anz32bha4p5ojxo0klal3iq0rpkhea"
TWITCH_USERNAME = "ninjaloutre"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 138020178406408192  # Remplace par l’ID de ton serveur
ROLE_NAME = "Joviaux Soyeux"
OWNER_ID = 127513232746348544  # Ton ID Discord (pas le pseudo)

# === DISCORD SETUP ===
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# === TWITCH : récupère ton ID utilisateur ===
def get_twitch_user_id():
    headers = {
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}", headers=headers)
    return response.json()["data"][0]["id"]

# === TWITCH : récupère jusqu’à 2000 followers ===
def get_followers(user_id, max_followers=2000):
    followers = []
    cursor = None
    headers = {
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
        "Client-Id": TWITCH_CLIENT_ID
    }

    while len(followers) < max_followers:
        params = {"to_id": user_id, "first": 100}
        if cursor:
            params["after"] = cursor
        response = requests.get("https://api.twitch.tv/helix/users/follows", headers=headers, params=params)
        data = response.json()
        followers += [f["from_name"].lower() for f in data.get("data", [])]
        cursor = data.get("pagination", {}).get("cursor")
        if not cursor:
            break

    return followers

# === NOTIFICATION PRIVÉE ===
async def notify_owner(message):
    owner = await client.fetch_user(OWNER_ID)
    if owner:
        try:
            await owner.send(message)
        except Exception as e:
            print(f"❌ Erreur d'envoi DM : {e}")

# === BOUCLE PRINCIPALE ===
async def check_followers_loop():
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("❌ Serveur introuvable.")
        return

    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if not role:
        print(f"❌ Rôle '{ROLE_NAME}' introuvable.")
        return

    user_id = get_twitch_user_id()

    while not client.is_closed():
        try:
            followers = get_followers(user_id)
            print(f"🔄 {len(followers)} followers récupérés.")

            for member in guild.members:
                username = member.name.lower()
                has_role = role in member.roles
                is_follower = username in followers

                if is_follower and not has_role:
                    await member.add_roles(role)
                    print(f"✅ {username} a reçu le rôle.")
                    await notify_owner(f"✅ {member.mention} a été reconnu comme follower Twitch.")
                elif not is_follower and has_role:
                    await member.remove_roles(role)
                    print(f"❌ {username} a perdu le rôle.")
                    await notify_owner(f"❌ {member.mention} ne suit plus sur Twitch. Rôle retiré.")

        except Exception as e:
            print(f"❗ Erreur dans la boucle : {e}")

        await asyncio.sleep(300)  # toutes les 5 minutes

@client.event
async def on_ready():
    print(f"🤖 Connecté en tant que {client.user}")
    client.loop.create_task(check_followers_loop())

# === SI MEMBRE REJOINT ===
@client.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return

    user_id = get_twitch_user_id()
    followers = get_followers(user_id)

    if member.name.lower() in followers:
        role = discord.utils.get(member.guild.roles, name=ROLE_NAME)
        if role:
            await member.add_roles(role)
            await notify_owner(f"✅ {member.mention} a rejoint et a été reconnu comme follower Twitch.")

# === LANCEMENT ===
print("=== Lancement du bot ===")
if not DISCORD_TOKEN:
    print("❌ Le token DISCORD_TOKEN est manquant.")
    exit(1)

client.run(DISCORD_TOKEN)
