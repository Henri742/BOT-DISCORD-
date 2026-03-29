import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# URL CURINGA: Usando o modelo 'gemini-pro' que é o padrão universal do Google
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def chamar_gemini(pergunta):
    payload = {"contents": [{"parts": [{"text": pergunta}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=payload, headers=headers) as resp:
                data = await resp.json()
                print(f"DEBUG FINAL: {data}") # Aparece no Railway
                
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    msg = data.get('error', {}).get('message', 'Erro desconhecido')
                    return f"❌ Erro {resp.status}: {msg}"
    except Exception as e:
        return f"❌ Erro: {str(e)}"

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO ONLINE - TENTATIVA FINAL")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

bot.run(os.getenv("DISCORD_TOKEN"))