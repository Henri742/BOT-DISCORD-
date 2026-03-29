import discord
from discord.ext import commands
import aiohttp
import os
import json
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente
load_dotenv()

# 2. Configurações da API
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Esta é a URL mais completa e oficial possível para o modelo Flash
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 3. Função de conexão direta (HTTP)
async def chamar_gemini(pergunta):
    payload = {"contents": [{"parts": [{"text": pergunta}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=payload, headers=headers) as resp:
                data = await resp.json()
                # ESSA LINHA ABAIXO VAI FAZER APARECER NO LOG DO RAILWAY:
                print(f"RESPOSTA DO GOOGLE: {data}")
                
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"❌ Erro {resp.status}: {data.get('error', {}).get('message')}"
    except Exception as e:
        print(f"ERRO DE CONEXAO: {e}")
        return f"❌ Erro de conexão: {str(e)}"

# 4. Comandos do Bot
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("✅ GUSTAVO BOT ONLINE - MODO v1beta ATIVO")

@bot.tree.command(name="ai", description="Conversar com o Gustavo")
async def ai(interaction: discord.Interaction, pergunta: str):
    # O defer() é vital para o Discord não dar "Interaction Failed"
    await interaction.response.defer()
    
    resposta = await chamar_gemini(pergunta)
    
    # Envia a resposta final cortando se passar do limite do Discord
    await interaction.followup.send(resposta[:1950])

bot.run(os.getenv("DISCORD_TOKEN"))