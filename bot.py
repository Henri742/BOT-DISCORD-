import discord
from discord.ext import commands
from discord import app_commands
from google import genai
from google.genai import types
import os
import asyncio
import time
import json
import io
from dotenv import load_dotenv
from collections import defaultdict
from pypdf import PdfReader

# ========================
# CARREGAR ENV E CONFIG
# ========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Novo Cliente do Gemini (SDK 2026)
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-1.5-flash" 

# ========================
# MEMÓRIA PERSISTENTE
# ========================
MEMORY_FILE = "memory.json"

try:
    with open(MEMORY_FILE, "r") as f:
        user_memory = json.load(f)
except Exception:
    user_memory = {}

MEMORY_LIMIT = 10

def salvar_memoria():
    with open(MEMORY_FILE, "w") as f:
        json.dump(user_memory, f)

# ========================
# CONFIG BOT DISCORD
# ========================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

cooldowns = defaultdict(float)
COOLDOWN_TIME = 4

def anti_spam(user_id):
    now = time.time()
    if now - cooldowns[user_id] < COOLDOWN_TIME:
        return False
    cooldowns[user_id] = now
    return True

# ========================
# FUNÇÃO NÚCLEO GEMINI
# ========================
async def perguntar_gemini(user_id, pergunta, multimidia=None):
    history = user_memory.get(str(user_id), [])
    
    # Prepara o conteúdo (texto ou texto + mídia)
    if multimidia:
        contents = [pergunta, multimidia]
    else:
        # Monta o contexto da memória para o prompt
        history.append(f"Usuário: {pergunta}")
        if len(history) > MEMORY_LIMIT:
            history.pop(0)
        contents = "\n".join(history)

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents
        )
        resposta = response.text
    except Exception as e:
        print(f"ERRO GEMINI ({user_id}):", e)
        resposta = "❌ Erro ao processar sua solicitação."

    # Só salva na memória se for uma conversa de texto normal
    if not multimidia:
        history.append(f"Bot: {resposta}")
        user_memory[str(user_id)] = history
        salvar_memoria()

    return resposta[:1900]

# ========================
# COMANDOS
# ========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} online com SDK google-genai!")

@bot.tree.command(name="ai", description="Pergunte qualquer coisa")
async def ai(interaction: discord.Interaction, pergunta: str):
    if not anti_spam(interaction.user.id):
        return await interaction.response.send_message("⏳ Calma! Espere o cooldown.", ephemeral=True)
    
    await interaction.response.defer()
    resposta = await perguntar_gemini(interaction.user.id, pergunta)
    await interaction.followup.send(resposta)

@bot.tree.command(name="resolver_imagem", description="Resolver por imagem")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):
    await interaction.response.defer()
    img_bytes = await imagem.read()
    
    mídia = types.Part.from_bytes(data=img_bytes, mime_type=imagem.content_type)
    resposta = await perguntar_gemini(interaction.user.id, "Resolva passo a passo este exercício da imagem:", multimidia=mídia)
    await interaction.followup.send(resposta)

@bot.tree.command(name="resolver_pdf", description="Resolver de PDF")
async def resolver_pdf(interaction: discord.Interaction, pdf: discord.Attachment):
    await interaction.response.defer()
    file = await pdf.read()
    reader = PdfReader(io.BytesIO(file))
    texto = "".join([p.extract_text() for p in reader.pages])
    
    resposta = await perguntar_gemini(interaction.user.id, f"Resolva os exercícios deste PDF:\n{texto[:6000]}")
    await interaction.followup.send(resposta)

# Comandos de atalho (Explicar, Resolver, Código, etc)
@bot.tree.command(name="explicar", description="Explica algo simples")
async def explicar(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Explique de forma simples: {tema}"))

@bot.tree.command(name="prova", description="Gerar mini prova")
async def prova(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    p = f"Crie uma mini prova com 5 questões, 4 alternativas e gabarito sobre: {tema}"
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, p))

@bot.tree.command(name="helpgust", description="Comandos")
async def helpgust(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 GUSTAVO BOT", color=0x2ecc71)
    embed.add_field(name="Comandos", value="/ai, /explicar, /prova, /resolver_imagem, /resolver_pdf")
    await interaction.response.send_message(embed=embed)

# ========================
# EXECUÇÃO
# ========================
async def main():
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        print(f"⚠️ Erro: {e}. Reiniciando...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())