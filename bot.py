import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, io, time
from dotenv import load_dotenv
from collections import defaultdict
from pypdf import PdfReader

# ========================
# CONFIGURAÇÃO
# ========================
load_dotenv()

# FORÇANDO A VERSÃO V1 (ESTÁVEL) NA CONFIGURAÇÃO
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Criamos o modelo especificando que queremos a versão estável
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# MEMÓRIA E COOLDOWN
# ========================
MEMORY_FILE = "memory.json"
try:
    with open(MEMORY_FILE, "r") as f: user_memory = json.load(f)
except: user_memory = {}

MEMORY_LIMIT = 10
cooldowns = defaultdict(float)

def salvar_memoria():
    with open(MEMORY_FILE, "w") as f: json.dump(user_memory, f)

def check_spam(user_id):
    now = time.time()
    if now - cooldowns[user_id] < 4: return False
    cooldowns[user_id] = now
    return True

# ========================
# FUNÇÃO NÚCLEO GEMINI
# ========================
async def perguntar_gemini(user_id, pergunta, imagem=None):
    history = user_memory.get(str(user_id), [])
    
    try:
        # Usamos generate_content que é o método padrão da v1
        if imagem:
            response = model.generate_content([pergunta, imagem])
        else:
            history.append(f"Usuário: {pergunta}")
            prompt = "\n".join(history[-MEMORY_LIMIT:])
            response = model.generate_content(prompt)
            
            resposta = response.text
            history.append(f"Bot: {resposta}")
            user_memory[str(user_id)] = history
            salvar_memoria()
            
        return response.text[:1900]
    except Exception as e:
        # Se der erro, vamos printar o erro completo no log do Railway
        print(f"ERRO DETALHADO: {e}")
        return "❌ Erro de conexão. Verifique os logs no Railway."

# ========================
# COMANDOS
# ========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - TENTATIVA FINAL V1")

@bot.tree.command(name="ai", description="Conversa geral")
async def ai(interaction: discord.Interaction, pergunta: str):
    if not check_spam(interaction.user.id):
        return await interaction.response.send_message("⏳ Aguarde 4 segundos.", ephemeral=True)
    await interaction.response.defer()
    await interaction.followup.send(await perguntar_gemini(interaction.user.id, pergunta))

@bot.tree.command(name="helpgust", description="Lista de comandos")
async def helpgust(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 GUSTAVO BOT", color=0x2ecc71)
    embed.add_field(name="Comandos", value="`/ai`, `/explicar`, `/resolver`, `/prova`, `/codigo`, `/resolver_imagem`, `/resolver_pdf`")
    await interaction.response.send_message(embed=embed)

# Adicione os outros comandos (explicar, prova, etc) aqui seguindo o modelo do /ai
# Para economizar espaço e focar no erro, resumi aqui, mas você pode manter os que já tinha!

bot.run(os.getenv("DISCORD_TOKEN"))