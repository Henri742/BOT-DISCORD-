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

# Inicialização ultra simples para evitar o erro 404
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-1.5-flash"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# FUNÇÃO NÚCLEO
# ========================
async def perguntar_gemini(pergunta, midia=None):
    try:
        # Enviamos apenas o necessário para o modelo não dar erro de rota
        conteudo = [pergunta, midia] if midia else pergunta
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=conteudo
        )
        return response.text
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        return "❌ Erro ao conectar com o Gemini. Verifique se a chave de API no Railway está correta."

# ========================
# COMANDOS
# ========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE!")

@bot.tree.command(name="ai", description="Conversar com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resposta = await perguntar_gemini(pergunta)
    await interaction.followup.send(resposta[:1900])

@bot.tree.command(name="helpgust", description="Ver comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos disponíveis: `/ai`, `/resolver_imagem`, `/resolver_pdf`")

@bot.tree.command(name="resolver_imagem", description="Resolver por foto")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):
    await interaction.response.defer()
    from google.genai import types
    img_bytes = await imagem.read()
    midia = types.Part.from_bytes(data=img_bytes, mime_type=imagem.content_type)
    resposta = await perguntar_gemini("Resolva este exercício:", midia=midia)
    await interaction.followup.send(resposta[:1900])

# ========================
# RODAR BOT
# ========================
bot.run(os.getenv("DISCORD_TOKEN"))