import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, time
from dotenv import load_dotenv

load_dotenv()

# FORÇANDO A PORTA v1 (ESTÁVEL)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# O segredo: Não usamos apenas o nome, usamos o caminho completo da v1
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - PORTA v1 ATIVADA")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    try:
        # Chamada direta sem frescura de versão beta
        response = model.generate_content(pergunta)
        await interaction.followup.send(response.text[:1900])
    except Exception as e:
        print(f"ERRO NOS LOGS: {e}")
        await interaction.followup.send("❌ O Google ainda diz que não me conhece. Verifique a chave JESUS.")

bot.run(os.getenv("DISCORD_TOKEN"))