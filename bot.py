import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÃO DE CLASSE PARA O BOT ---
class GustavoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sincroniza os comandos de barra (Slash Commands)
        await self.tree.sync()
        print(f"[{datetime.datetime.now()}] 🔄 Comandos sincronizados com o Discord.")

bot = GustavoBot()

# --- BANCO DE DADOS EM MEMÓRIA (Simulado) ---
usuarios_xp = {} # {user_id: xp}

termos_tech = {
    "API": "Application Programming Interface. É a ponte que faz dois softwares conversarem.",
    "Frontend": "A parte visual do site, o que o usuário vê e clica.",
    "Backend": "O 'cérebro' do site. Onde fica a lógica e o banco de dados.",
    "Git": "Sistema de controle de versão. É a máquina do tempo do seu código.",
    "Deploy": "O ato de colocar o seu código para rodar em um servidor real (como o Railway)."
}

erros_python = {
    "NameError": "Variável não definida. Você chamou algo que não criou.",
    "SyntaxError": "Erro de escrita. Confira parênteses, aspas e dois-pontos.",
    "IndentationError": "Espaçamento errado. O Python exige 4 espaços de recuo.",
    "TypeError": "Tipos incompatíveis. Ex: somar texto com número."
}

# --- EVENTOS ---
@bot.event
async def on_ready():
    print(f"--- GUSTAVO ULTIMATE ONLINE ---")
    print(f"Logado como: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"-------------------------------")
    await bot.change_presence(activity=discord.Game(name="Codando em Python 3.11"))

# --- COMANDO 1: DICIONÁRIO TECH ---
@bot.tree.command(name="glossario", description="Dicionário de termos de programação")
@app_commands.describe(termo="O termo que você quer entender")
async def glossario(interaction: discord.Interaction, termo: str):
    busca = termo.capitalize()
    definicao = termos_tech.get(busca, "Ainda não tenho esse termo no meu banco de dados.")
    
    embed = discord.Embed(title=f"📖 Glossário: {busca}", color=0x9b59b6)
    embed.description = definicao
    await interaction.response.send_message(embed=embed)

# --- COMANDO 2: EXPLICAÇÃO DE ERROS (Aprimorado) ---
@bot.tree.command(name="guia_erro", description="Entenda o que o erro do Python quer te dizer")
async def guia_erro(interaction: discord.Interaction, erro: str):
    # Busca flexível (procura parte do nome do erro)
    resultado = "Erro não catalogado. Tente copiar apenas o nome principal (ex: NameError)."
    for k, v in erros_python.items():
        if k.lower() in erro.lower():
            resultado = v
            break
            
    embed = discord.Embed(title="🚨 Analisador de Erros", color=0xe74c3c)
    embed.add_field(name="Diagnóstico:", value=resultado)
    await interaction.response.send_message(embed=embed)

# --- COMANDO 3: SISTEMA DE DESAFIOS COM XP ---
@bot.tree.command(name="treinar", description="Receba um desafio e ganhe XP")
async def treinar(interaction: discord.Interaction):
    desafios = [
        "Crie uma função que conte vogais em uma frase.",
        "Faça um programa que verifique se um ano é bissexto.",
        "Crie um conversor de Celsius para Fahrenheit.",
        "Desenvolva um jogo de Pedra, Papel e Tesoura no terminal."
    ]
    
    user_id = interaction.user.id
    usuarios_xp[user_id] = usuarios_xp.get(user_id, 0) + 10
    
    embed = discord.Embed(title="🎯 Desafio de Treinamento", color=0x2ecc71)
    embed.description = random.choice(desafios)
    embed.add_field(name="Recompensa:", value="10 XP acumulados!")
    embed.set_footer(text=f"Seu XP atual: {usuarios_xp[user_id]}")
    
    await interaction.response.send_message(embed=embed)

# --- COMANDO 4: UTILITÁRIO (LIMPAR CHAT) ---
@bot.tree.command(name="limpar", description="Limpa mensagens do canal (Apenas Admins)")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: int):
    await interaction.response.send_message(f"Limpando {quantidade} mensagens...", ephemeral=True)
    await interaction.channel.purge(limit=quantidade)

# --- COMANDO 5: STATUS DO SERVIDOR ---
@bot.tree.command(name="status", description="Veja informações do bot e do servidor")
async def status(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 Status do Sistema", color=0x34495e)
    embed.add_field(name="Ping (Latência):", value=f"{round(bot.latency * 1000)}ms")
    embed.add_field(name="Usuários Ativos:", value=str(len(bot.users)))
    embed.set_footer(text=f"Servidor: {interaction.guild.name}")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))