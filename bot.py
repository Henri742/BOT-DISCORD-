import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import asyncio
import time
from dotenv import load_dotenv
from collections import defaultdict

# ========================
# CARREGAR ENV
# ========================

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# ========================
# CONFIG BOT
# ========================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# MEMÓRIA DE CONVERSA
# ========================

user_memory = defaultdict(list)

MEMORY_LIMIT = 10

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

    history = user_memory[user_id]

    history.append(f"Usuário: {pergunta}")

    if len(history) > MEMORY_LIMIT:
        history.pop(0)

    prompt = "\n".join(history)

    try:

        response = model.generate_content(prompt)

        resposta = response.text

    except Exception as e:

        resposta = "❌ Erro ao falar com a IA."

    history.append(f"Bot: {resposta}")

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
# /HELP
# ========================

@bot.tree.command(name="help", description="Mostrar comandos")
async def help(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🤖 Bot Gemini",
        description="Comandos disponíveis",
        color=0x2ecc71
    )

    embed.add_field(
        name="/ai",
        value="Pergunte qualquer coisa para a IA",
        inline=False
    )

    embed.add_field(
        name="/explicar",
        value="Explica um tema",
        inline=False
    )

    embed.add_field(
        name="/resolver",
        value="Resolve exercícios",
        inline=False
    )

    embed.add_field(
        name="/codigo",
        value="Gerar código",
        inline=False
    )

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