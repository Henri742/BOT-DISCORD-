import discord
from discord.ext import commands
from google import genai
import os, json, io, time
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()

# CONFIGURAÇÃO GOOGLE SDK 2026
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# PROTEÇÃO DE MEMÓRIA: Se não existir, o bot não quebra mais!
MEMORY_FILE = "memory.json"
user_memory = {}

if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            user_memory = json.load(f)
    except:
        user_memory = {}

def salvar_memoria():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(user_memory, f)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

# FUNÇÃO NÚCLEO
async def perguntar_gemini(pergunta):
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=pergunta
        )
        return response.text
    except Exception as e:
        print(f"ERRO NO GEMINI: {e}")
        return "❌ Erro de conexão com o Google."

# COMANDOS
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE E OPERACIONAL!")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await perguntar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

@bot.tree.command(name="helpgust", description="Comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos: `/ai`, `/helpgust`")

bot.run(os.getenv("DISCORD_TOKEN"))