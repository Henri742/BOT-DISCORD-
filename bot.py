import discord
from discord.ext import commands
import google.generativeai as genai
import os, json
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÃO
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Usando o modelo flash (mais rápido e estável)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# MEMÓRIA SIMPLES
user_memory = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - O GEMINI FINAL!")

@bot.tree.command(name="ai", description="Conversar com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    
    try:
        # Recupera o que foi dito antes
        history = user_memory.get(str(interaction.user.id), "")
        prompt_completo = f"{history}\nUsuário: {pergunta}"
        
        response = model.generate_content(prompt_completo)
        resposta_texto = response.text
        
        # Salva na memória (últimas conversas)
        user_memory[str(interaction.user.id)] = f"Usuário: {pergunta}\nBot: {resposta_texto}"[-1000:]
        
        await interaction.followup.send(resposta_texto[:1900])
        
    except Exception as e:
        print(f"ERRO: {e}")
        await interaction.followup.send(f"❌ Erro: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))