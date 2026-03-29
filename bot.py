import discord
from discord.ext import commands
import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Forçamos a URL da versão estável V1 na mão!
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def chamar_gemini_direto(pergunta):
    payload = {
        "contents": [{"parts": [{"text": pergunta}]}]
    }
    headers = {'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                # Extrai o texto da resposta do Google
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                erro_texto = await resp.text()
                print(f"ERRO API: {resp.status} - {erro_texto}")
                return f"❌ Erro na API do Google ({resp.status}). Verifique se a chave JESUS está ativa."

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ GUSTAVO BOT ONLINE - VIA CONEXÃO DIRETA V1")

@bot.tree.command(name="ai", description="Conversar com o Gustavo")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini_direto(pergunta)
    await interaction.followup.send(resposta[:1900])

bot.run(os.getenv("DISCORD_TOKEN"))