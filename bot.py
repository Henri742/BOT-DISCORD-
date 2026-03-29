import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, io, time
from dotenv import load_dotenv
from pypdf import PdfReader

# ========================
# CONFIGURAÇÃO
# ========================
load_dotenv()

# Configuração simples que evita erros de versão
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# FUNÇÃO DE RESPOSTA (SIMPLIFICADA)
# ========================
async def perguntar_gemini(pergunta):
    try:
        # Enviamos apenas a string direta para evitar o erro 400 de argumento inválido
        response = model.generate_content(pergunta)
        return response.text
    except Exception as e:
        print(f"ERRO NOS LOGS: {e}")
        return "❌ O Google recebeu o pedido, mas algo deu errado. Tente novamente em instantes."

# ========================
# COMANDOS
# ========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - CONEXÃO VALIDADA!")

@bot.tree.command(name="ai", description="Conversar com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await perguntar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

@bot.tree.command(name="helpgust", description="Ver comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos ativos: `/ai`, `/helpgust`")

bot.run(os.getenv("DISCORD_TOKEN"))