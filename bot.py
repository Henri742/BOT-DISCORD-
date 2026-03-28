import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import asyncio
import time
import json
import io
from dotenv import load_dotenv
from collections import defaultdict
from pypdf import PdfReader

# ========================
# CARREGAR ENV
# ========================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# ========================
# MEMÓRIA PERSISTENTE
# ========================

MEMORY_FILE = "memory.json"

try:
    with open(MEMORY_FILE, "r") as f:
        user_memory = json.load(f)
except:
    user_memory = {}

MEMORY_LIMIT = 10

def salvar_memoria():
    with open(MEMORY_FILE, "w") as f:
        json.dump(user_memory, f)

# ========================
# CONFIG BOT
# ========================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# ANTI SPAM
# ========================

cooldowns = defaultdict(float)
COOLDOWN_TIME = 4

def anti_spam(user_id):

    now = time.time()

    if now - cooldowns[user_id] < COOLDOWN_TIME:
        return False

    cooldowns[user_id] = now
    return True

# ========================
# FUNÇÃO GEMINI
# ========================

async def perguntar_gemini(user_id, pergunta):

    history = user_memory.get(str(user_id), [])

    history.append(f"Usuário: {pergunta}")

    if len(history) > MEMORY_LIMIT:
        history.pop(0)

    prompt = "\n".join(history)

    try:

        response = model.generate_content(prompt)

        resposta = response.text

    except Exception as e:

        print("ERRO GEMINI:", e)

        resposta = "❌ Erro ao falar com a IA."

    history.append(f"Bot: {resposta}")

    user_memory[str(user_id)] = history

    salvar_memoria()

    return resposta[:1900]

# ========================
# BOT ONLINE
# ========================

@bot.event
async def on_ready():

    await bot.tree.sync()

    print(f"✅ Bot conectado como {bot.user}")

# ========================
# /AI
# ========================

@bot.tree.command(name="ai", description="Pergunte qualquer coisa")
async def ai(interaction: discord.Interaction, pergunta: str):

    if not anti_spam(interaction.user.id):

        await interaction.response.send_message(
            "⏳ Espere alguns segundos antes de usar novamente.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    resposta = await perguntar_gemini(interaction.user.id, pergunta)

    await interaction.followup.send(resposta)

# ========================
# /EXPLICAR
# ========================

@bot.tree.command(name="explicar", description="Explica algo simples")
async def explicar(interaction: discord.Interaction, tema: str):

    await interaction.response.defer()

    prompt = f"Explique de forma simples: {tema}"

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /RESOLVER
# ========================

@bot.tree.command(name="resolver", description="Resolver exercícios")
async def resolver(interaction: discord.Interaction, problema: str):

    await interaction.response.defer()

    prompt = f"Resolva passo a passo: {problema}"

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /CODIGO
# ========================

@bot.tree.command(name="codigo", description="Gerar código")
async def codigo(interaction: discord.Interaction, pedido: str):

    await interaction.response.defer()

    prompt = f"Gere código para: {pedido}"

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /RESUMO
# ========================

@bot.tree.command(name="resumo", description="Fazer resumo de texto")
async def resumo(interaction: discord.Interaction, texto: str):

    await interaction.response.defer()

    prompt = f"Faça um resumo simples para estudar:\n{texto}"

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /PROVA
# ========================

@bot.tree.command(name="prova", description="Gerar mini prova")
async def prova(interaction: discord.Interaction, tema: str):

    await interaction.response.defer()

    prompt = f"""
Crie uma mini prova com:

5 questões
4 alternativas
gabarito no final

Tema: {tema}
"""

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /RESOLVER IMAGEM
# ========================

@bot.tree.command(name="resolver_imagem", description="Resolver exercício por imagem")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):

    await interaction.response.defer()

    image_bytes = await imagem.read()

    try:

        response = model.generate_content(
            [
                "Resolva esse exercício passo a passo",
                {
                    "mime_type": "image/png",
                    "data": image_bytes
                }
            ]
        )

        resposta = response.text[:1900]

    except Exception as e:

        print("ERRO IMAGEM:", e)

        resposta = "❌ Erro ao analisar a imagem."

    await interaction.followup.send(resposta)

# ========================
# /RESOLVER PDF
# ========================

@bot.tree.command(name="resolver_pdf", description="Resolver exercícios de PDF")
async def resolver_pdf(interaction: discord.Interaction, pdf: discord.Attachment):

    await interaction.response.defer()

    file = await pdf.read()

    reader = PdfReader(io.BytesIO(file))

    texto = ""

    for page in reader.pages:
        texto += page.extract_text()

    prompt = f"Resolva os exercícios deste PDF:\n{texto[:6000]}"

    resposta = await perguntar_gemini(interaction.user.id, prompt)

    await interaction.followup.send(resposta)

# ========================
# /HELPGUST
# ========================

@bot.tree.command(name="helpgust", description="Mostrar comandos do bot")
async def helpgust(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🤖 GUSTAVO BOT - Comandos",
        description="Lista de comandos disponíveis",
        color=0x2ecc71
    )

    embed.add_field(name="/ai", value="Pergunte qualquer coisa para a IA", inline=False)
    embed.add_field(name="/explicar", value="Explica algo simples", inline=False)
    embed.add_field(name="/resolver", value="Resolver exercícios", inline=False)
    embed.add_field(name="/codigo", value="Gerar código", inline=False)
    embed.add_field(name="/resumo", value="Criar resumo de texto", inline=False)
    embed.add_field(name="/prova", value="Gerar mini prova", inline=False)
    embed.add_field(name="/resolver_imagem", value="Resolver exercícios por imagem", inline=False)
    embed.add_field(name="/resolver_pdf", value="Resolver exercícios de PDF", inline=False)

    embed.set_footer(text="IA Gemini Flash")

    await interaction.response.send_message(embed=embed)

# ========================
# ANTI CRASH
# ========================

async def start():

    while True:

        try:

            await bot.start(DISCORD_TOKEN)

        except Exception as e:

            print("⚠️ Bot caiu. Reiniciando em 10 segundos...")

            await asyncio.sleep(10)

asyncio.run(start())