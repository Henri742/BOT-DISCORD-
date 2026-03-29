import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# A URL direta para a versão estável v1 (sem beta!)
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def chamar_gemini(pergunta):
    payload = {
        "contents": [{"parts": [{"text": pergunta}]}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                erro = await resp.text()
                return f"❌ Erro na API: {resp.status}\n{erro[:100]}"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ GUSTAVO BOT ONLINE - VIA HTTP DIRETO")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

bot.run(os.getenv("DISCORD_TOKEN"))