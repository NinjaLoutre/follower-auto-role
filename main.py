import discord
import requests
import os
import asyncio

# --- PARAMÈTRES TWITCH ---
TWITCH_CLIENT_ID = "29hnvf3ru8waz788a3yqfaxyb67krw"
TWITCH_ACCESS_TOKEN = "anz32bha4p5ojxo0klal3iq0rpkhea"
TWITCH_USERNAME = "nedile"  # à adapter si ton pseudo est différent

# --- PARAMÈTRES DISCORD ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 138020178406408192  # à remplacer par l’ID de ton serveur Discord
ROLE_NAME = "Joviaux Soyeux"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# --- Obtenir l’ID Twitch de l'utilisateur ---
def get_twitch_user_id():
    headers = {
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}", headers=headers)
    return response.json()["data"][0]["id"]

# --- Obtenir les followers de la chaîne Twitch ---
def get_followers(user_id):
    headers = {
        "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    response = requests.get(f"https://api.twitch.tv/helix/users/follows?to_id={user_id}&first=100", headers=headers)
    return [f["from_name"].lower() for f in response.json().get("data", [])]

# --- Tâche régulière ---
async def check_followers_loop():
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("❌ Impossible de trouver le serveur.")
        return

    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if not role:
        print(f"❌ Rôle '{ROLE_NAME}' introuvable.")
        return

    user_id = get_twitch_user_id()
    print(f"🎯 Twitch User ID : {user_id}")

    while not client.is_closed():
        try:
            followers = get_followers(user_id)
            print(f"🔁 {len(followers)} followers récupérés.")

            for member in guild.members:
                username = member.name.lower()
                has_role = role in member.roles
                is_follower = username in followers

                if is_follower and not has_role:
                    await member.add_roles(role)
                    print(f"✅ Ajouté : {username}")
                elif not is_follower and has_role:
                    await member.remove_roles(role)
                    print(f"❌ Retiré : {username}")

        except Exception as e:
            print(f"❗ Erreur : {e}")

        await asyncio.sleep(300)  # toutes les 5 minutes

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    client.loop.create_task(check_followers_loop())

# --- Lancement ---
print("=== Démarrage du bot ===")
if not DISCORD_TOKEN:
    print("❌ Le token DISCORD_TOKEN est manquant.")
    exit(1)

client.run(DISCORD_TOKEN)
