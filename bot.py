import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, time
from dotenv import load_dotenv

# ========================
# CONFIGURAÇÃO
# ========================
load_dotenv()

# Configuração simples com a chave "JESUS"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# FUNÇÃO DE RESPOSTA
# ========================
async def perguntar_gemini(pergunta):
    try:
        response = model.generate_content(pergunta)
        return response.text
    except Exception as e:
        print(f"ERRO NOS LOGS: {e}")
        return "❌ O erro 404 persiste. Verifique se a chave no Railway é a correta."

# ========================
# COMANDOS
# ========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE COM A CHAVE JESUS!")

@bot.tree.command(name="ai", description="Conversar com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await perguntar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

@bot.tree.command(name="helpgust", description="Ver comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos: `/ai`, `/helpgust`")

bot.run(os.getenv("DISCORD_TOKEN"))