import discord
import asyncio
import os

print("=== Début du script ===")

token = os.getenv("DISCORD_TOKEN")
if not token:
    print("❌ Le token DISCORD_TOKEN est manquant.")
    exit(1)
else:
    print("✅ Le token DISCORD_TOKEN est présent.")

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    await client.close()  # Ferme le bot juste après connexion

client.run(token)
