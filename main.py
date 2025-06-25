import os
import discord
import requests
import asyncio
import json

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")

GUILD_ID = '138020178406408192'  # Remplacer par l'ID réel de ton serveur
ROLE_NAME = 'Joviaux Soyeux'
LINKED_FILE = 'linked_users.json'


def get_followers():
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {TWITCH_TOKEN}'
    }
    url = f'https://api.twitch.tv/helix/users/follows?to_id=TON_ID_TWITCH'
    response = requests.get(url, headers=headers)
    return [follow['from_id'] for follow in response.json().get('data', [])]


def load_links():
    if not os.path.exists(LINKED_FILE):
        return {}
    with open(LINKED_FILE, 'r') as f:
        return json.load(f)


def save_links(data):
    with open(LINKED_FILE, 'w') as f:
        json.dump(data, f)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    await check_followers()


@client.event
async def on_message(message):
    if message.guild is None and message.content.startswith('!linktwitch'):
        links = load_links()
        discord_id = str(message.author.id)
        twitch_username = message.content.split(' ')[1] if len(message.content.split(' ')) > 1 else None
        if twitch_username:
            links[discord_id] = twitch_username
            save_links(links)
            await message.channel.send(f"🔗 Ton compte Twitch **{twitch_username}** est maintenant lié à ton compte Discord.")
        else:
            await message.channel.send("❌ Syntaxe : `!linktwitch pseudo_twitch`")


async def check_followers():
    await client.wait_until_ready()
    guild = client.get_guild(int(GUILD_ID))
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    followers = get_followers()
    links = load_links()

    for member in guild.members:
        discord_id = str(member.id)
        twitch_user = links.get(discord_id)
        if twitch_user:
            is_follower = True  # à remplacer par vraie vérif si besoin
            if is_follower:
                if role not in member.roles:
                    await member.add_roles(role)
                    await member.send(f"🌟 Tu as reçu le rôle **{ROLE_NAME}** car tu es abonné à Ninja Loutre sur Twitch.")
            else:
                if role in member.roles:
                    await member.remove_roles(role)
                    await member.send(f"❌ Le rôle **{ROLE_NAME}** t’a été retiré car tu n’es plus follower sur Twitch.")


client.run(DISCORD_TOKEN)
