import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# URL forçando a v1 estável. Se a JESUS estiver certa, aqui não tem erro!
# Tente esta URL exata (algumas contas exigem o modelo sem o prefixo 'models/' na v1)
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def chamar_gemini(pergunta):
    payload = {"contents": [{"parts": [{"text": pergunta}]}]}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"❌ Erro {resp.status}: {data.get('error', {}).get('message', 'Erro desconhecido')}"
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ BOT ONLINE - USANDO PYTHON ESTÁVEL NO RAILWAY")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

bot.run(os.getenv("DISCORD_TOKEN"))