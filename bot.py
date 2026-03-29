import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# URL FORÇANDO A VERSÃO V1 (A que a chave JESUS aceita)
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def chamar_gemini_direto(pergunta):
    payload = {
        "contents": [{"parts": [{"text": pergunta}]}]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    erro_msg = await resp.text()
                    print(f"ERRO API: {resp.status} - {erro_msg}")
                    return f"❌ Erro {resp.status}: O Google recusou a conexão. Verifique se a chave no Railway não tem espaços antes ou depois."
    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ GUSTAVO BOT ONLINE - MODO SEGURO ATIVADO")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini_direto(pergunta)
    await interaction.followup.send(resposta[:1900])

bot.run(os.getenv("DISCORD_TOKEN"))