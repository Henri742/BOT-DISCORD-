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

# Novo Cliente SDK 2026
client = genai.Client(api_key=GEMINI_API_KEY)

# Ajuste do MODEL_ID com prefixo para evitar Erro 404
MODEL_ID = "models/gemini-1.5-flash" 

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
    
    # Se houver imagem/arquivo, enviamos sem o histórico para evitar confusão do modelo
    if multimidia:
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
        print(f"ERRO GEMINI NO USUÁRIO {user_id}: {e}")
        resposta = "❌ Erro ao processar sua solicitação no servidor do Google."

    # Salva na memória apenas conversas de texto
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
    print(f"✅ {bot.user} online com SDK google-genai!")

@bot.tree.command(name="ai", description="Chat livre com a IA")
async def ai(interaction: discord.Interaction, pergunta: str):
    if not anti_spam(interaction.user.id):
        return await interaction.response.send_message("⏳ Espere 4 segundos entre as mensagens.", ephemeral=True)
    
    await interaction.response.defer()
    resposta = await perguntar_gemini(interaction.user.id, pergunta)
    await interaction.followup.send(resposta)

@bot.tree.command(name="explicar", description="Explica um tema de forma simples")
async def explicar(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    prompt = f"Explique de forma muito simples e didática: {tema}"
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, prompt))

@bot.tree.command(name="resolver", description="Resolve exercícios passo a passo")
async def resolver(interaction: discord.Interaction, problema: str):
    await interaction.response.defer()
    prompt = f"Resolva passo a passo, explicando a lógica: {problema}"
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, prompt))

@bot.tree.command(name="codigo", description="Gera ou analisa códigos")
async def codigo(interaction: discord.Interaction, pedido: str):
    await interaction.response.defer()
    prompt = f"Aja como um programador sênior. {pedido}"
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, prompt))

@bot.tree.command(name="prova", description="Gera uma mini prova de 5 questões")
async def prova(interaction: discord.Interaction, tema: str):
    await interaction.response.defer()
    prompt = f"Crie uma mini prova sobre {tema} com 5 questões de múltipla escolha e o gabarito no final."
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, prompt))

@bot.tree.command(name="resolver_imagem", description="Resolve exercício por foto")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):
    await interaction.response.defer()
    img_bytes = await imagem.read()
    
    # Formatação correta para o novo SDK
    midia = types.Part.from_bytes(data=img_bytes, mime_type=imagem.content_type)
    resposta = await perguntar_gemini(interaction.user.id, "Resolva este exercício da imagem detalhadamente:", multimidia=midia)
    await interaction.followup.send(resposta)

@bot.tree.command(name="resolver_pdf", description="Lê e resolve questões de um PDF")
async def resolver_pdf(interaction: discord.Interaction, pdf: discord.Attachment):
    await interaction.response.defer()
    file = await pdf.read()
    reader = PdfReader(io.BytesIO(file))
    texto_completo = ""
    for page in reader.pages:
        texto_completo += page.extract_text()
    
    prompt = f"Analise o texto deste PDF e resolva os exercícios encontrados:\n{texto_completo[:6000]}"
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, prompt))

@bot.tree.command(name="helpgust", description="Mostra o guia de comandos")
async def helpgust(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 GUSTAVO BOT - Guia de Ajuda",
        description="Dúvidas? Aqui estão meus comandos:",
        color=0x2ecc71
    )
    embed.add_field(name="💬 Chat", value="`/ai`: Conversa geral com memória.", inline=False)
    embed.add_field(name="📖 Estudo", value="`/explicar`: Resumos didáticos.\n`/resolver`: Problemas escritos.\n`/prova`: Mini simulados.", inline=False)
    embed.add_field(name="📁 Arquivos", value="`/resolver_imagem`: Mande foto da questão.\n`/resolver_pdf`: Analisa documentos PDF.", inline=False)
    embed.add_field(name="💻 Dev", value="`/codigo`: Ajuda com programação.", inline=False)
    embed.set_footer(text="IA: Gemini 1.5 Flash")
    await interaction.response.send_message(embed=embed)

# ========================
# START
# ========================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)