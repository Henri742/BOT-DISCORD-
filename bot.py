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
# CONFIGURAÇÕES INICIAIS
# ========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cliente padrão (funciona melhor com chaves do AI Studio)
client = genai.Client(api_key=GEMINI_API_KEY)

# ID do modelo padrão estável
MODEL_ID = "gemini-1.5-flash" 

# ========================
# MEMÓRIA PERSISTENTE
# ========================
MEMORY_FILE = "memory.json"

try:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            user_memory = json.load(f)
    else:
        user_memory = {}
except:
    user_memory = {}

MEMORY_LIMIT = 10

def salvar_memoria():
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(user_memory, f)
    except Exception as e:
        print(f"Erro ao salvar memória: {e}")

# ========================
# CONFIG BOT DISCORD
# ========================
intents = discord.Intents.default()
intents.message_content = True 
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
    
    if multimidia:
        # Para imagens/arquivos, ignoramos o histórico para evitar erro de contexto
        contents = [pergunta, multimidia]
    else:
        # Chat normal com memória
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
        print(f"ERRO GEMINI ({user_id}): {e}")
        resposta = "❌ Ocorreu um erro na comunicação com a IA. Verifique os logs."

    if not multimidia:
        history.append(f"Bot: {resposta}")
        user_memory[str(user_id)] = history
        salvar_memoria()

    return resposta[:1900]

# ========================
# COMANDOS SLASH (/)
# ========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} ONLINE E PRONTO!")

@bot.tree.command(name="ai", description="Chat livre com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    if not anti_spam(interaction.user.id):
        return await interaction.response.send_message("⏳ Aguarde 4 segundos.", ephemeral=True)
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, pergunta))

@bot.tree.command(name="explicar", description="Explica um tema")
async def explicar(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Explique de forma simples: {tema}"))

@bot.tree.command(name="resolver", description="Resolve exercícios")
async def resolver(interaction: discord.Interaction, problema: str):
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Resolva passo a passo: {problema}"))

@bot.tree.command(name="codigo", description="Gera ou analisa códigos")
async def codigo(interaction: discord.Interaction, pedido: str):
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Aja como programador: {pedido}"))

@bot.tree.command(name="prova", description="Gera mini prova")
async def prova(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Crie prova de 5 questões sobre: {tema}"))

@bot.tree.command(name="resolver_imagem", description="Resolve por foto")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):
    await interaction.response.defer()
    img_bytes = await imagem.read()
    midia = types.Part.from_bytes(data=img_bytes, mime_type=imagem.content_type)
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, "Resolva a imagem:", multimidia=midia))

@bot.tree.command(name="resolver_pdf", description="Lê e resolve PDF")
async def resolver_pdf(interaction: discord.Interaction, pdf: discord.Attachment):
    await interaction.response.defer()
    file = await pdf.read()
    reader = PdfReader(io.BytesIO(file))
    texto = "".join([p.extract_text() for p in reader.pages])
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, f"Resolva o PDF:\n{texto[:6000]}"))

@bot.tree.command(name="helpgust", description="Guia de ajuda")
async def helpgust(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 GUSTAVO BOT", description="Aqui estão meus comandos:", color=0x2ecc71)
    embed.add_field(name="Estudo", value="`/ai`, `/explicar`, `/resolver`, `/prova`", inline=False)
    embed.add_field(name="Arquivos", value="`/resolver_imagem`, `/resolver_pdf`", inline=False)
    embed.add_field(name="Outros", value="`/codigo`", inline=False)
    await interaction.response.send_message(embed=embed)

# ========================
# EXECUÇÃO
# ========================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)