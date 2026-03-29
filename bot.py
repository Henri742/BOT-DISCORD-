import discord
from discord.ext import commands
from google import genai
import os, json, io
from dotenv import load_dotenv
from pypdf import PdfReader

# ========================
# CONFIGURAÇÃO
# ========================
load_dotenv()

# O SEGREDO: Criamos o cliente SEM especificar nada de v1beta
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# FUNÇÃO NÚCLEO
# ========================
async def perguntar_gemini(pergunta):
    try:
        # Usamos o método mais moderno do SDK 2026
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=pergunta
        )
        return response.text
    except Exception as e:
        # Se der erro, vamos ver exatamente qual é no log
        print(f"ERRO NO GEMINI: {e}")
        return "❌ Erro de conexão. Verifique os logs no Railway."

# ========================
# COMANDOS
# ========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - SDK 2026 ATIVO")

@bot.tree.command(name="ai", description="Conversar com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await perguntar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

@bot.tree.command(name="helpgust", description="Ver comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos: `/ai`, `/helpgust`")

bot.run(os.getenv("DISCORD_TOKEN"))