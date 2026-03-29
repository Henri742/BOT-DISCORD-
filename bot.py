import discord
from discord.ext import commands
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import os, json, time
from dotenv import load_dotenv

load_dotenv()

# 1. Configura a chave JESUS
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. Cria o modelo forçando a versão estável v1
# Isso evita que ele tente o v1beta do Projeto Robo
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - ROTA v1")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    try:
        # RequestOptions(api_version='v1') é o segredo para ignorar o erro 404
        response = model.generate_content(
            pergunta, 
            request_options=RequestOptions(api_version='v1')
        )
        await interaction.followup.send(response.text[:1900])
    except Exception as e:
        print(f"ERRO NO LOG: {e}")
        await interaction.followup.send("❌ Erro de conexão. Verifique se a chave JESUS está correta no Railway.")

bot.run(os.getenv("DISCORD_TOKEN"))