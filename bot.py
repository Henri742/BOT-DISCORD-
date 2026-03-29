import discord
from discord.ext import commands
import google.generativeai as genai
import os, json, time
from dotenv import load_dotenv

# 1. Carrega as variáveis (GEMINI_API_KEY e DISCORD_TOKEN)
load_dotenv()

# 2. Configura a API com a sua chave
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 3. Definimos o modelo usando o prefixo 'models/' que é o padrão da v1 estável
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    # Sincroniza os comandos de barra (/) com o Discord
    await bot.tree.sync()
    print(f"✅ GUSTAVO BOT ONLINE - ROTA ESTÁVEL")

@bot.tree.command(name="ai", description="Conversar com o Gustavo")
async def ai(interaction: discord.Interaction, pergunta: str):
    # O defer() avisa ao Discord para esperar a IA pensar (evita o 'Interaction Failed')
    await interaction.response.defer()
    
    try:
        # Chamada direta e limpa ao Gemini
        response = model.generate_content(pergunta)
        
        # Envia a resposta final
        await interaction.followup.send(response.text[:1900])
        
    except Exception as e:
        # Se der qualquer erro, ele será printado no log do Railway e no Discord
        print(f"ERRO NO GEMINI: {e}")
        await interaction.followup.send(f"❌ Erro na IA: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))