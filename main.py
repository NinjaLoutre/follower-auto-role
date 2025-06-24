import discord
import asyncio
import os

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")

    # Exemple : boucle toutes les 10 minutes
    while True:
        print("🔄 Vérification fictive des followers Twitch...")
        await asyncio.sleep(600)  # toutes les 10 minutes

# Token stocké dans les variables d’environnement
client.run(os.getenv("DISCORD_TOKEN"))