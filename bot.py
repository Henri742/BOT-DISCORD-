import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 📚 BANCO DE DADOS ACADÊMICO (Expansível para +10.000 linhas)
# ==========================================

# Módulo 1: Lógica Matemática (Prof. Anderlan)
CONTEUDO_MATEMATICA = {
    "Aula 01 - Introdução": "🔌 **Álgebra Booleana:** Criada por George Boole. Base dos circuitos digitais. Trabalha com binários (V/F).\n\n**Aplicações:**\n• Teoria dos Grafos (Redes, GPS)\n• Criptografia\n• Análise de Complexidade.",
    "Aula 02 - Axiomas": "⚖️ **O que é Proposição?** Sentença com sentido completo que pode ser V ou F.\n\n**Axiomas Fundamentais:**\n1. **Não Contradição:** Não pode ser V e F ao mesmo tempo.\n2. **Terceiro Excluído:** Ou é V ou é F, não há terceira opção.\n\n**Tipos:** Simples (Atômicas) e Compostas (Moleculares).",
    "Aula 03 - Conectivos": "🔗 **Operações Lógicas:**\n• `~` (Negação): Inverte o valor lógico.\n• `^` (Conjunção / E): Só é V se TUDO for V.\n• `v` (Disjunção / OU): É V se PELO MENOS UM for V.\n• `->` (Condicional): A regra de ouro é a 'Vera Fischer' -> Só é Falso se V -> F.\n• `<->` (Bicondicional): É V se os valores forem iguais.",
    "Aula 04 - Tabelas Verdade": "📊 **Construindo a Tabela:**\n• **Fórmula de Linhas:** $2^n$ (n = nº de proposições). Ex: p, q, r = $2^3 = 8$ linhas.\n• **Dica de Preenchimento:** A 1ª coluna alterna na metade (ex: 4V, 4F). A 2ª coluna de 2 em 2. A 3ª de 1 em 1.\n• **Ordem de Resolução:** Parênteses > Negação > Conjunção/Disjunção > Condicional/Bicondicional."
}

# Módulo 2: Lógica de Programação (Prof. Marcelo)
CONTEUDO_PROGRAMACAO = {
    "Aula 01/02 - Algoritmos": "🏗️ **O que é um Algoritmo?** Sequência finita de passos para resolver um problema.\n\n**Representações Gráficas:**\n• **Fluxograma:** Losango = Decisão, Retângulo = Processo.\n• **Pseudocódigo (Portugol):** Escrita estruturada.\n• **Diagrama de Nassi-Shneiderman:** Blocos aninhados.\n• **Método Jackson e Warnier-Orr:** Focados em estrutura de dados.",
    "Aula 03/04 - Repetições": "🔄 **Estruturas de Controle de Fluxo:**\n• **Para...até (For):** Usado quando você sabe o número exato de repetições.\n• **Enquanto (While):** Repete enquanto a condição for V. Testa antes de executar.\n• **Repita...até:** Executa o bloco pelo menos uma vez, testa a condição no final.",
    "Aula 05 - Intro Python": "🐍 **Fundamentos do Python:**\n• **Tipagem Dinâmica:** Você não precisa declarar se a variável é inteira ou texto, o Python descobre sozinho.\n• `type(x)`: Retorna o tipo da variável.\n• `input()`: Pede dados ao usuário (sempre retorna String).\n• `print()`: Exibe na tela.\n• `#`: Cria um comentário no código.",
    "Aula 06 - Condicionais": "🔀 **Tomada de Decisão em Python:**\n• `if` (Se): Testa a primeira condição.\n• `elif` (Senão se): Testa condições intermediárias.\n• `else` (Senão): O que acontece se tudo der falso.\n\n*Nota do Prof:* O Python é rígido com a indentação (os 4 espaços dentro do `if`)."
}

# Questões Retiradas Diretamente dos PDFs
QUESTOES_PROVAS = [
    {"p": "Qual a 'regra de ouro' para identificar uma Condicional (->) falsa?", "r": "Só é falsa se o antecedente for Verdadeiro e o consequente for Falso (V -> F).", "materia": "mat"},
    {"p": "Se tivermos 3 proposições (p, q, r), quantas linhas terá a tabela verdade?", "r": "Terá 8 linhas (Fórmula: 2 elevado a n).", "materia": "mat"},
    {"p": "Em Python, o tipo de uma variável é definido dinamicamente em tempo de execução. Verdadeiro ou Falso?", "r": "Verdadeiro. O Python é de tipagem dinâmica.", "materia": "prog"},
    {"p": "Qual estrutura de repetição deve ser usada quando sabemos previamente o número de vezes que o bloco será executado?", "r": "A estrutura 'Para... até' (For).", "materia": "prog"}
]

# ==========================================
# ⚙️ CORE DO BOT E EVENTOS
# ==========================================

class GustavoBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.xp_database = {}

    async def setup_hook(self):
        await self.tree.sync()
        print(f"[{datetime.datetime.now()}] 🟢 SISTEMA LEVIATÃ ONLINE E SINCRONIZADO.")

bot = GustavoBot()

# ==========================================
# 🖥️ COMPONENTES DE INTERFACE (UI)
# ==========================================

class DropdownEstudo(discord.ui.Select):
    def __init__(self, materia):
        self.materia = materia
        banco = CONTEUDO_MATEMATICA if materia == "mat" else CONTEUDO_PROGRAMACAO
        options = [discord.SelectOption(label=k) for k in banco.keys()]
        super().__init__(placeholder="Selecione o capítulo para ler o resumo...", options=options)

    async def callback(self, interaction: discord.Interaction):
        banco = CONTEUDO_MATEMATICA if self.materia == "mat" else CONTEUDO_PROGRAMACAO
        embed = discord.Embed(title=f"📖 {self.values[0]}", description=banco[self.values[0]], color=0x3498db)
        await interaction.response.edit_message(embed=embed)

class PainelEstudo(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="Lógica Matemática", style=discord.ButtonStyle.primary, emoji="📐")
    async def mat(self, i: discord.Interaction, b: discord.ui.Button):
        v = discord.ui.View().add_item(DropdownEstudo("mat"))
        await i.response.send_message("Módulos de Lógica Matemática:", view=v, ephemeral=True)

    @discord.ui.button(label="Lógica de Programação", style=discord.ButtonStyle.success, emoji="💻")
    async def prog(self, i: discord.Interaction, b: discord.ui.Button):
        v = discord.ui.View().add_item(DropdownEstudo("prog"))
        await i.response.send_message("Módulos de Lógica de Programação:", view=v, ephemeral=True)

class ModalCalculadora(discord.ui.Modal, title='Sistema de Avaliação (Aula 06)'):
    nome = discord.ui.TextInput(label='Nome do Aluno', placeholder='Digite seu nome')
    n1 = discord.ui.TextInput(label='Nota 1', placeholder='Ex: 7.5')
    n2 = discord.ui.TextInput(label='Nota 2', placeholder='Ex: 6.0')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nota1 = float(self.n1.value.replace(',', '.'))
            nota2 = float(self.n2.value.replace(',', '.'))
            media = (nota1 + nota2) / 2
            
            # Lógica exata exigida no Exercício 1 da Aula 06 do Prof. Marcelo
            if media >= 7.0:
                sit = "✅ APROVADO"
                cor = 0x2ecc71
            elif media >= 4.0:
                sit = "⚠️ REAVALIAÇÃO"
                cor = 0xf1c40f
            else:
                sit = "❌ REPROVADO"
                cor = 0xe74c3c

            embed = discord.Embed(title=f"Boletim de {self.nome.value}", color=cor)
            embed.add_field(name="Nota 1", value=nota1)
            embed.add_field(name="Nota 2", value=nota2)
            embed.add_field(name="Média Final", value=f"**{media:.1f}**", inline=False)
            embed.add_field(name="Situação", value=sit, inline=False)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ Erro: Por favor, digite apenas números nas notas.", ephemeral=True)

# ==========================================
# 🚀 COMANDOS DO BOT (SLASH COMMANDS)
# ==========================================

@bot.tree.command(name="hub", description="Abre o painel central de estudos e resumos.")
async def hub(interaction: discord.Interaction):
    embed = discord.Embed(title="🏛️ Hub Acadêmico Gustavo", description="Acesse os resumos completos das disciplinas abaixo:", color=0x9b59b6)
    embed.set_footer(text="Baseado no material dos Profs. Anderlan e Marcelo")
    await interaction.response.send_message(embed=embed, view=PainelEstudo())

@bot.tree.command(name="simulado", description="Sorteia uma questão das listas de exercícios dos PDFs.")
async def simulado(interaction: discord.Interaction):
    questao = random.choice(QUESTOES_PROVAS)
    embed = discord.Embed(title="📝 Questão de Prova", description=questao['p'], color=0xe67e22)
    
    uid = interaction.user.id
    bot.xp_database[uid] = bot.xp_database.get(uid, 0) + 50
    embed.set_footer(text=f"Recompensa: +50 XP | XP Total: {bot.xp_database[uid]}")

    class ViewGabarito(discord.ui.View):
        @discord.ui.button(label="Mostrar Gabarito", style=discord.ButtonStyle.secondary)
        async def ver(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message(f"✅ **Gabarito:** {questao['r']}", ephemeral=True)

    await interaction.response.send_message(embed=embed, view=ViewGabarito())

@bot.tree.command(name="calculadora", description="Calcula a média e situação do aluno (Lógica Aula 06).")
async def calculadora(interaction: discord.Interaction):
    await interaction.response.send_modal(ModalCalculadora())

@bot.tree.command(name="pomodoro", description="Inicia um cronômetro de foco de 25 minutos.")
async def pomodoro(interaction: discord.Interaction):
    await interaction.response.send_message(f"🍅 **Modo Foco Ativado!** {interaction.user.mention}, concentre-se nos estudos. Te aviso em 25 minutos.")
    await asyncio.sleep(1500) # 25 minutos em segundos
    await interaction.followup.send(f"⏰ {interaction.user.mention}, 25 minutos concluídos! Faça uma pausa de 5 minutos.")

@bot.tree.command(name="limpar_chat", description="Apaga mensagens do canal (Requer permissão de Admin).")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar_chat(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    apagadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 {len(apagadas)} mensagens varridas do servidor.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Aulas de Python"))

bot.run(os.getenv("DISCORD_TOKEN"))