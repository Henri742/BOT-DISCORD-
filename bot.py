import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, io, time
from dotenv import load_dotenv
from collections import defaultdict
from pypdf import PdfReader

load_dotenv()

# CONFIGURAÇÃO GOOGLE (BIBLIOTECA ESTÁVEL)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# CONFIGURAÇÃO DISCORD
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# MEMÓRIA
MEMORY_FILE = "memory.json"
try:
    with open(MEMORY_FILE, "r") as f: user_memory = json.load(f)
except: user_memory = {}

def salvar_memoria():
    with open(MEMORY_FILE, "w") as f: json.dump(user_memory, f)

# FUNÇÃO NÚCLEO
async def perguntar_gemini(user_id, pergunta, imagem=None):
    history = user_memory.get(str(user_id), [])
    
    try:
        if imagem:
            # Resolução com imagem
            response = model.generate_content([pergunta, imagem])
        else:
            # Chat com memória
            history.append(f"Usuário: {pergunta}")
            prompt = "\n".join(history[-10:]) # Últimas 10 mensagens
            response = model.generate_content(prompt)
            
            resposta = response.text
            history.append(f"Bot: {resposta}")
            user_memory[str(user_id)] = history
            salvar_memoria()
            
        return response.text[:1900]
    except Exception as e:
        print(f"ERRO: {e}")
        return "❌ Erro ao conectar. Verifique se a API Key está correta no Railway."

# COMANDOS
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE (VERSÃO ESTÁVEL)")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resp = await perguntar_gemini(interaction.user.id, pergunta)
    await interaction.followup.send(resp)

@bot.tree.command(name="resolver_imagem", description="Resolver por foto")
async def resolver_imagem(interaction: discord.Interaction, imagem: discord.Attachment):
    await interaction.response.defer()
    img_data = await imagem.read()
    img_part = {"mime_type": imagem.content_type, "data": img_data}
    resp = await perguntar_gemini(interaction.user.id, "Resolva este exercício passo a passo:", imagem=img_part)
    await interaction.followup.send(resp)

@bot.tree.command(name="helpgust", description="Comandos")
async def helpgust(interaction: discord.Interaction):
    await interaction.response.send_message("🤖 Comandos: `/ai`, `/resolver_imagem`, `/explicar`...")

bot.run(os.getenv("DISCORD_TOKEN"))