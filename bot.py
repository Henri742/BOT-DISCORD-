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
# 📚 MEGA BANCO DE DADOS ACADÊMICO
# ==========================================

CONTEUDO_MATEMATICA = {
    "Aula 01 - Introdução e Álgebra": (
        "🔌 **Álgebra Booleana:** Criada por George Boole no séc. XIX. É a base dos circuitos digitais modernos.\n\n"
        "**Aplicações na Computação:**\n"
        "• **Teoria dos Grafos:** Rotas de GPS e Redes Sociais.\n"
        "• **Criptografia:** Segurança de dados via Teoria dos Números.\n"
        "• **Análise de Complexidade:** Medir eficiência de algoritmos de larga escala."
    ),
    "Aula 02 - Axiomas e Proposições": (
        "⚖️ **Proposição:** Sentença declarativa com sentido completo que pode ser Verdadeira (V) ou Falsa (F).\n\n"
        "**Axiomas (Princípios) Fundamentais:**\n"
        "1. **Não Contradição:** Uma proposição não pode ser V e F ao mesmo tempo.\n"
        "2. **Terceiro Excluído:** Ou é V ou é F, não existe 'talvez' (Lógica Bivalente).\n\n"
        "**Tipos:** Atômicas (Simples) e Moleculares (Compostas)."
    ),
    "Aula 03 - Operadores e Conectivos": (
        "🔗 **Operações Lógicas Básicas:**\n"
        "• `~` **(Negação):** O 'do contra'. Inverte o valor (V vira F, F vira V).\n"
        "• `^` **(Conjunção / E):** Extremamente exigente. Só é V se **TUDO** for V.\n"
        "• `v` **(Disjunção / OU):** Mais flexível. É V se **PELO MENOS UM** for V.\n"
        "• `->` **(Condicional):** Regra da 'Vera Fischer'. Só é Falso no caso V -> F.\n"
        "• `<->` **(Bicondicional):** O espelho. Só é V se ambos forem **IGUAIS**."
    ),
    "Aula 04 - Tabelas Verdade (Visual)": (
        "📊 **Construindo a Tabela (O Passo a Passo):**\n"
        "A fórmula para descobrir o número de linhas é $2^n$ (n = nº de proposições).\n"
        "A regra de ouro é resolver de **dentro para fora** (Parênteses > Negação > E/OU).\n\n"
        "**Exemplo Prático: ~ ( p ^ ~q )**\n"
        "```text\n"
        "| 1. p | 1. q | 2. ~q | 3. p ^ ~q | 4. ~(p ^ ~q) |\n"
        "|------|------|-------|-----------|--------------|\n"
        "|   V  |   V  |   F   |     F     |       V      |\n"
        "|   V  |   F  |   V   |     V     |       F      |\n"
        "|   F  |   V  |   F   |     F     |       V      |\n"
        "|   F  |   F  |   V   |     F     |       V      |\n"
        "```\n"
        "💡 *Lembre-se: A resposta final da expressão é sempre a última coluna!*"
    )
}

CONTEUDO_PROGRAMACAO = {
    "Módulo 01 - Algoritmos": (
        "🏗️ **O que é um Algoritmo?**\n"
        "É uma sequência finita de passos bem definidos para resolver um problema.\n\n"
        "**Representações (Como desenhar a ideia):**\n"
        "• **Fluxograma:** Usa formas geométricas (Losango = Decisão, Retângulo = Processamento).\n"
        "• **Pseudocódigo (Portugol):** Escrita em português estruturado.\n"
        "• **Diagrama de Nassi-Shneiderman:** Blocos que se encaixam.\n"
        "• **Métodos Jackson / Warnier-Orr:** Foco na estrutura dos dados."
    ),
    "Módulo 02 - Repetições (Loops)": (
        "🔄 **Estruturas de Controle de Fluxo:**\n"
        "O computador é ótimo em repetir tarefas sem cansar. Usamos:\n\n"
        "• **Para...até (For):** Ideal para quando você **já sabe** quantas vezes vai repetir (ex: contar de 1 a 10).\n"
        "• **Enquanto (While):** Repete o bloco de código **enquanto** uma condição for Verdadeira. Ele testa antes de fazer.\n"
        "• **Repita...até (Do-While):** Ele faz a ação pelo menos uma vez e só testa a condição no final."
    ),
    "Módulo 03 - Python Básico": (
        "🐍 **Fundamentos da Linguagem Python:**\n"
        "• **Tipagem Dinâmica:** Você não precisa avisar que a variável é texto ou número. O Python é inteligente e descobre sozinho.\n"
        "• `print('texto')`: Joga a informação na tela do usuário.\n"
        "• `input()`: Pausa o programa e pede para o usuário digitar algo (Sempre devolve um Texto/String).\n"
        "• `type(variavel)`: Te conta qual é o tipo de dado guardado ali.\n"
        "• `#`: O jogo-da-velha cria um comentário. O computador ignora essa linha."
    ),
    "Módulo 04 - Python Condicionais": (
        "🔀 **Tomada de Decisão (Aula 06):**\n"
        "Em Python, usamos a identação (4 espaços) para definir quem está dentro de quem.\n\n"
        "• `if` (Se): O primeiro teste.\n"
        "• `elif` (Senão se): Testes intermediários (ex: se a nota for maior que 4 E menor que 7).\n"
        "• `else` (Senão): O 'lixo' da condição. Se tudo acima for falso, ele executa o else automaticamente."
    )
}

CONTEUDO_PYTHON_GUIAS = {
    "Funções Nativas": (
        "🛠️ **Caixa de Ferramentas Python:**\n\n"
        "• `int()`: Converte um texto para número inteiro. Super útil logo após um `input()`.\n"
        "• `float()`: Converte para número quebrado (decimal).\n"
        "• `len()`: 'Length'. Conta quantos itens tem numa lista ou letras numa palavra.\n"
        "• `sum()`: Soma todos os números dentro de uma lista de uma vez só."
    ),
    "Guia de Erros 1 - SyntaxError": (
        "❌ **SyntaxError (Erro de Sintaxe):**\n"
        "O computador não entendeu a sua gramática. \n"
        "**Como resolver:** Verifique se você esqueceu de fechar um parênteses `)`, se esqueceu as aspas `\"\"` em um texto, ou se esqueceu os dois pontos `:` no final de um `if`, `for` ou `while`."
    ),
    "Guia de Erros 2 - NameError": (
        "❌ **NameError (Erro de Nome):**\n"
        "Você chamou o Batman, mas ele não está na caverna.\n"
        "**Como resolver:** Você tentou usar uma variável ou função que não foi criada antes. Verifique se você digitou o nome corretamente (Python diferencia Maiúsculas de minúsculas)."
    ),
    "Guia de Erros 3 - TypeError": (
        "❌ **TypeError (Erro de Tipo):**\n"
        "Mistura de água com óleo.\n"
        "**Como resolver:** Você tentou fazer uma operação impossível, como somar o texto `'Henrique'` com o número `10`. Use `str()` ou `int()` para deixar todo mundo do mesmo tipo antes de operar."
    ),
    "Termos Tech Básicos": (
        "🌐 **Dicionário do Programador:**\n"
        "• **Deploy:** Colocar seu projeto online num servidor (ex: Railway).\n"
        "• **Frontend:** A interface gráfica bonita do site.\n"
        "• **Backend:** O motor, o banco de dados, o que roda por trás.\n"
        "• **API:** O garçom que leva o pedido do Frontend para o Backend."
    )
}

QUESTOES_PROVAS = [
    {"p": "Lógica Mat: Qual a 'regra de ouro' para identificar uma Condicional (->) falsa?", "r": "Só é falsa no caso Vera Fischer: Antecedente Verdadeiro e Consequente Falso (V -> F)."},
    {"p": "Lógica Mat: Se tivermos 3 proposições (p, q, r), quantas linhas terá a tabela verdade?", "r": "Terá 8 linhas. A fórmula é 2 elevado a 'n' (2³ = 8)."},
    {"p": "Lógica Mat: Qual o nome do princípio que diz que uma proposição não pode ser V e F ao mesmo tempo?", "r": "Princípio da Não Contradição."},
    {"p": "Prog: Qual a finalidade de um Losango em um Fluxograma?", "r": "Representar uma Tomada de Decisão (Estrutura Condicional)."},
    {"p": "Prog: Qual estrutura de repetição deve ser usada quando sabemos previamente o número exato de repetições?", "r": "A estrutura 'Para... até' (For)."},
    {"p": "Python: A função input() retorna por padrão qual tipo de dado?", "r": "Retorna sempre uma String (Texto), mesmo que o usuário digite um número."}
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
        print(f"[{datetime.datetime.now()}] 🟢 SISTEMA LEVIATÃ (VERSÃO OMNISCIENTE) ONLINE.")

bot = GustavoBot()

# ==========================================
# 🖥️ COMPONENTES DE INTERFACE (HUB)
# ==========================================

class DropdownEstudo(discord.ui.Select):
    def __init__(self, categoria):
        self.categoria = categoria
        if categoria == "mat": banco = CONTEUDO_MATEMATICA
        elif categoria == "prog": banco = CONTEUDO_PROGRAMACAO
        else: banco = CONTEUDO_PYTHON_GUIAS
            
        options = [discord.SelectOption(label=k) for k in banco.keys()]
        super().__init__(placeholder="Selecione um tópico para estudar...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.categoria == "mat": banco = CONTEUDO_MATEMATICA
        elif self.categoria == "prog": banco = CONTEUDO_PROGRAMACAO
        else: banco = CONTEUDO_PYTHON_GUIAS
            
        embed = discord.Embed(title=f"📖 {self.values[0]}", description=banco[self.values[0]], color=0x2c3e50)
        await interaction.response.edit_message(embed=embed)

class PainelEstudo(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="Lógica Matemática (Anderlan)", style=discord.ButtonStyle.primary, emoji="📐", row=0)
    async def mat(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Matemática:", view=discord.ui.View().add_item(DropdownEstudo("mat")), ephemeral=True)

    @discord.ui.button(label="Lógica de Programação (Marcelo)", style=discord.ButtonStyle.success, emoji="💻", row=0)
    async def prog(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Programação:", view=discord.ui.View().add_item(DropdownEstudo("prog")), ephemeral=True)

    @discord.ui.button(label="Guia Python & Erros", style=discord.ButtonStyle.danger, emoji="🐍", row=1)
    async def python(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("Módulos de Python:", view=discord.ui.View().add_item(DropdownEstudo("py")), ephemeral=True)

# Modal da Calculadora (Aula 06)
class ModalCalculadora(discord.ui.Modal, title='Boletim Universitário'):
    nome = discord.ui.TextInput(label='Nome do Aluno', placeholder='Digite seu nome')
    n1 = discord.ui.TextInput(label='Nota 1', placeholder='Ex: 7.5')
    n2 = discord.ui.TextInput(label='Nota 2', placeholder='Ex: 6.0')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nota1 = float(self.n1.value.replace(',', '.'))
            nota2 = float(self.n2.value.replace(',', '.'))
            media = (nota1 + nota2) / 2
            
            if media >= 7.0: sit, cor = "✅ APROVADO", 0x2ecc71
            elif media >= 4.0: sit, cor = "⚠️ REAVALIAÇÃO (Recuperação)", 0xf1c40f
            else: sit, cor = "❌ REPROVADO", 0xe74c3c

            embed = discord.Embed(title=f"🎓 Boletim: {self.nome.value}", color=cor)
            embed.add_field(name="Nota 1", value=nota1)
            embed.add_field(name="Nota 2", value=nota2)
            embed.add_field(name="Média Final", value=f"**{media:.1f}**", inline=False)
            embed.add_field(name="Situação", value=sit, inline=False)
            await interaction.response.send_message(embed=embed)
        except ValueError:
            await interaction.response.send_message("❌ Erro: Digite apenas números! (Use ponto ou vírgula)", ephemeral=True)

# ==========================================
# 🚀 COMANDOS DO BOT (SLASH COMMANDS)
# ==========================================

@bot.tree.command(name="hub", description="O painel central de estudos. Acesse todo o conhecimento do bot.")
async def hub(interaction: discord.Interaction):
    embed = discord.Embed(title="🏛️ Hub Acadêmico Gustavo", description="Escolha a disciplina nos botões abaixo para abrir o seu material de estudo interativo.", color=0x9b59b6)
    embed.set_thumbnail(url=bot.user.display_avatar.url if bot.user.display_avatar else None)
    await interaction.response.send_message(embed=embed, view=PainelEstudo())

@bot.tree.command(name="simulado", description="Ganhe XP respondendo questões reais das aulas.")
async def simulado(interaction: discord.Interaction):
    q = random.choice(QUESTOES_PROVAS)
    uid = interaction.user.id
    bot.xp_database[uid] = bot.xp_database.get(uid, 0) + 50
    
    embed = discord.Embed(title="📝 Questão Aleatória", description=q['p'], color=0xe67e22)
    embed.set_footer(text=f"⭐ Você ganhou 50 XP! Seu XP Total: {bot.xp_database[uid]}")

    class ViewGab(discord.ui.View):
        @discord.ui.button(label="Mostrar Gabarito", style=discord.ButtonStyle.secondary)
        async def ver(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message(f"✅ **Resposta Correta:**\n{q['r']}", ephemeral=True)

    await interaction.response.send_message(embed=embed, view=ViewGab())

@bot.tree.command(name="calculadora", description="Calcula média e diz se você passou (Baseado na Aula 06).")
async def calculadora(interaction: discord.Interaction):
    await interaction.response.send_modal(ModalCalculadora())

@bot.tree.command(name="pomodoro", description="Inicia timer de 25 minutos para você focar nos estudos.")
async def pomodoro(interaction: discord.Interaction):
    await interaction.response.send_message(f"🍅 **Modo Foco Iniciado!** {interaction.user.mention}, concentre-se. O bot vai te chamar em 25 minutos.")
    await asyncio.sleep(1500)
    await interaction.followup.send(f"⏰ {interaction.user.mention}, o tempo acabou! Faça uma pausa de 5 minutos, você merece.")

@bot.tree.command(name="status", description="Veja suas estatísticas de estudo no servidor.")
async def status(interaction: discord.Interaction):
    xp = bot.xp_database.get(interaction.user.id, 0)
    embed = discord.Embed(title="📊 Status do Estudante", color=0x34495e)
    embed.add_field(name="Nível Atual", value=f"✨ Lvl {xp // 100}")
    embed.add_field(name="XP Total", value=f"⭐ {xp} XP")
    embed.add_field(name="Latência (Ping)", value=f"📡 {round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="limpar_chat", description="Deleta várias mensagens de uma vez (Apenas Admins).")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar_chat(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    apagadas = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 Chat limpo. {len(apagadas)} mensagens deletadas.", ephemeral=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Aulas de Programação"))

bot.run(os.getenv("DISCORD_TOKEN"))