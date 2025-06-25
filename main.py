import discord
import json
import requests
import asyncio
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
ROLE_NAME = "Joviaux Soyeux"

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

@client.event
async def on_ready():
    print("=== Bot démarré ===")
    print(f"Connecté en tant que {client.user}")

    await check_followers()

async def check_followers():
    print("🔄 Vérification des followers Twitch...")
    followers_cache = load_json("followers.json", {"followers": []})
    linked_users = load_json("linked_users.json", {})

    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {TWITCH_TOKEN}"
    }
    user_info = requests.get("https://api.twitch.tv/helix/users", headers=headers).json()
    user_id = user_info["data"][0]["id"]
    url = f"https://api.twitch.tv/helix/users/follows?to_id={user_id}&first=100"

    response = requests.get(url, headers=headers).json()
    twitch_followers = [f["from_name"].lower() for f in response["data"]]

    guild = discord.utils.get(client.guilds)
    if not guild:
        print("❌ Serveur Discord introuvable.")
        return

    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if not role:
        print("❌ Rôle introuvable sur le serveur.")
        return

    for member_id, twitch_name in linked_users.items():
        member = guild.get_member(int(member_id))
        if not member:
            continue

        has_followed = twitch_name.lower() in twitch_followers
        has_role = role in member.roles

        if has_followed and not has_role:
            await member.add_roles(role)
            try:
                await member.send("✅ Merci de suivre sur Twitch ! Tu as reçu le rôle **Joviaux Soyeux** sur Discord.")
            except:
                pass
        elif not has_followed and has_role:
            await member.remove_roles(role)
            try:
                await member.send("❌ Tu ne suis plus sur Twitch. Le rôle **Joviaux Soyeux** t’a été retiré.")
            except:
                pass

    followers_cache["followers"] = twitch_followers
    save_json("followers.json", followers_cache)

@client.event
async def on_message(message):
    if not isinstance(message.channel, discord.DMChannel):
        return

    if message.content.startswith("!linktwitch"):
        parts = message.content.split()
        if len(parts) != 2:
            await message.channel.send("❌ Utilisation correcte : `!linktwitch ton_pseudo_twitch`")
            return

        twitch_name = parts[1].lower()
        linked_users = load_json("linked_users.json", {})
        linked_users[str(message.author.id)] = twitch_name
        save_json("linked_users.json", linked_users)
        await message.channel.send(f"🔗 Ton compte Twitch **{twitch_name}** est maintenant lié à ton compte Discord.")

client.run(DISCORD_TOKEN)
