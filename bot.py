import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

# 1. Carrega as variáveis
load_dotenv()

# 2. Configurações da API
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# Usando a URL mais específica possível (v1beta + flash-latest)
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"

# 3. CONFIGURAÇÃO DAS INTENTS (Onde estava o erro!)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 4. Função de conexão direta
async def chamar_gemini(pergunta):
    payload = {
        "contents": [{"parts": [{"text": pergunta}]}]
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(URL, json=payload, headers=headers) as resp:
                data = await resp.json()
                
                # Debug no log do Railway
                print(f"RESPOSTA DO GOOGLE: {data}")
                
                if resp.status == 200:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    msg = data.get('error', {}).get('message', 'Erro desconhecido')
                    return f"❌ Erro {resp.status}: {msg}"
                    
    except Exception as e:
        print(f"ERRO DE CONEXAO: {e}")
        return f"❌ Erro de conexão: {str(e)}"

# 5. Comandos
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ BOT ONLINE - LOGADO COMO {bot.user}")

@bot.tree.command(name="ai", description="Conversar com o Gustavo")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await chamar_gemini(pergunta)
    await interaction.followup.send(resposta[:1950])

bot.run(os.getenv("DISCORD_TOKEN"))