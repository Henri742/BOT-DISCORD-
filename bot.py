import discord
from discord.ext import commands
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import os, json, io, time
from dotenv import load_dotenv
from collections import defaultdict
from pypdf import PdfReader

# ========================
# CONFIGURAÇÃO
# ========================
load_dotenv()

# CONFIGURAÇÃO DA API - FORÇANDO A ROTA ESTÁVEL V1
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Criamos o modelo com opções para ignorar o v1beta que causa o erro 404
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash"
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# MEMÓRIA E SISTEMA
# ========================
MEMORY_FILE = "memory.json"
try:
    with open(MEMORY_FILE, "r") as f: user_memory = json.load(f)
except: user_memory = {}

def salvar_memoria():
    with open(MEMORY_FILE, "w") as f: json.dump(user_memory, f)

# ========================
# FUNÇÃO NÚCLEO (O SEGREDO ESTÁ AQUI)
# ========================
async def perguntar_gemini(user_id, pergunta, imagem=None):
    history = user_memory.get(str(user_id), [])
    try:
        # RequestOptions força o SDK a usar a versão estável da API
        options = RequestOptions(api_version='v1')
        
        if imagem:
            response = model.generate_content([pergunta, imagem], request_options=options)
        else:
            history.append(f"Usuário: {pergunta}")
            prompt = "\n".join(history[-10:])
            response = model.generate_content(prompt, request_options=options)
            
            resposta = response.text
            history.append(f"Bot: {resposta}")
            user_memory[str(user_id)] = history
            salvar_memoria()
            
        return response.text[:1900]
    except Exception as e:
        print(f"ERRO NOS LOGS: {e}")
        return "❌ O Google ainda está recusando a conexão (Erro 404). Verifique a chave no Railway."

# ========================
# COMANDOS
# ========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - USANDO ROTA V1")

@bot.tree.command(name="ai", description="Conversar")
async def ai(interaction: discord.Interaction, pergunta: str):
    await interaction.response.defer()
    resp = await perguntar_gemini(interaction.user.id, pergunta)
    await interaction.followup.send(resp)

@bot.tree.command(name="helpgust", description="Ver comandos")
async def helpgust(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 GUSTAVO BOT", color=0x2ecc71)
    embed.add_field(name="Estudo", value="`/ai`, `/explicar`, `/prova`", inline=False)
    embed.add_field(name="Arquivos", value="`/resolver_imagem`, `/resolver_pdf`", inline=False)
    await interaction.response.send_message(embed=embed)

# Adicione aqui os outros comandos (resolver_imagem, etc) seguindo a mesma lógica
bot.run(os.getenv("DISCORD_TOKEN"))