import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, time
from dotenv import load_dotenv

# 1. Carrega as chaves do Railway
load_dotenv()

# 2. Configura a API com a sua chave JESUS
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Usamos o nome completo do modelo para não ter erro 404
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Sincroniza os comandos / com o Discord
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - ROTA ESTÁVEL")

@bot.tree.command(name="ai", description="Conversar com o Gustavo")
async def ai(interaction: discord.Interaction, pergunta: str):
    # O defer() avisa ao Discord para esperar a IA pensar (evita o "Interaction Failed")
    await interaction.response.defer()
    
    try:
        # Chamada limpa ao Gemini
        response = model.generate_content(pergunta)
        
        # Envia a resposta (cortando se for maior que 1900 caracteres)
        await interaction.followup.send(response.text[:1900])
        
    except Exception as e:
        print(f"ERRO NO GEMINI: {e}")
        # Se der erro, ele avisa no Discord qual foi o problema
        await interaction.followup.send(f"❌ Erro: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))