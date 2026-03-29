import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- BASE DE DADOS LOCAL (Desafios) ---
desafios = [
    "Crie uma função que receba um número e diga se ele é par ou ímpar.",
    "Faça um código que inverta uma palavra (Ex: 'Python' vira 'nohtyP').",
    "Crie uma lista de 5 frutas e use um loop 'for' para imprimir cada uma.",
    "Escreva um programa que calcule a média de 3 notas de um aluno.",
    "Crie um dicionário que represente um carro (marca, modelo, ano)."
]

# --- BASE DE DADOS LOCAL (Explicação de Erros) ---
explica_erros = {
    "NameError": "Você tentou usar uma variável ou função que não existe ou ainda não foi criada.",
    "SyntaxError": "Há um erro de digitação no seu código. Verifique parênteses, aspas ou dois-pontos.",
    "IndentationError": "O Python é rígido com os espaços! Verifique se o recuo do seu código está correto.",
    "TypeError": "Você tentou fazer uma operação com tipos que não combinam (ex: somar texto com número).",
    "IndexError": "Você tentou acessar uma posição em uma lista que não existe."
}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ GUSTAVO MENTOR ONLINE - PRONTO PARA ESTUDAR!")

# --- COMANDO 1: EXPLICADOR DE ERROS ---
@bot.tree.command(name="erro", description="Explica um erro de programação")
async def erro(interaction: discord.Interaction, nome_do_erro: str):
    # Procura o erro na nossa base ou dá uma resposta genérica
    explicacao = explica_erros.get(nome_do_erro, "Não encontrei esse erro específico, mas verifique a ortografia ou se faltou importar algo.")
    
    embed = discord.Embed(title=f"❓ Entendendo o {nome_do_erro}", description=explicacao, color=0x3498db)
    embed.add_field(name="Dica:", value="Sempre leia a última linha do erro no seu terminal!")
    await interaction.response.send_message(embed=embed)

# --- COMANDO 2: DESAFIO DIÁRIO ---
@bot.tree.command(name="desafio", description="Manda um desafio de lógica para você")
async def desafio(interaction: discord.Interaction):
    desafio_escolhido = random.choice(desafios)
    
    embed = discord.Embed(title="💻 Desafio de Hoje", description=desafio_escolhido, color=0x2ecc71)
    embed.set_footer(text="Tente resolver sem copiar da internet! 🚀")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))